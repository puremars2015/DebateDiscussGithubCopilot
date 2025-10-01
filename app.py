from flask import Flask, jsonify, request, g, render_template, redirect, url_for
from datetime import datetime
import os
from extensions import db, migrate

app = Flask(__name__, template_folder='templates', static_folder='static')
BASE_DIR = os.path.dirname(__file__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-secret'

# initialize extensions
db.init_app(app)
migrate.init_app(app, db)

# import models and utils after extensions initialized to avoid circular import
from models import User, DebateTopic, Debate, Round, Vote, MatchHistory
from utils import calculate_elo, compute_round_result

@app.context_processor
def inject_now():
    from datetime import datetime
    return {'current_year': datetime.utcnow().year}


@app.route('/')
def index():
    # support optional query params: show=pending, page=n
    show = request.args.get('show')
    page = int(request.args.get('page', 1))
    per_page = 8
    q = DebateTopic.query
    if show == 'pending':
        q = q.filter(DebateTopic.status=='pending')
    else:
        q = q.filter(DebateTopic.status=='approved')
    topics = q.order_by(DebateTopic.created_at.desc()).limit(per_page).offset((page-1)*per_page).all()
    return render_template('index.html', topics=topics)


@app.route('/login')
def login_page():
    return render_template('login.html')


@app.route('/apply')
def apply_page():
    return render_template('apply.html')


@app.route('/topics/<int:topic_id>')
def topic_page(topic_id):
    t = DebateTopic.query.get_or_404(topic_id)
    return render_template('topic_detail.html', topic=t)


@app.route('/api/auth/login', methods=['POST'])
def login():
    # For MVP: accept a JSON {"line_id": "...", "nickname": "..."}
    data = request.get_json() or {}
    line_id = data.get('line_id')
    nickname = data.get('nickname') or 'Guest'
    if not line_id:
        return jsonify({'error':'line_id required'}), 400
    user = User.query.filter_by(line_id=line_id).first()
    if not user:
        user = User(line_id=line_id, nickname=nickname, join_date=datetime.utcnow())
        db.session.add(user)
        db.session.commit()
    # return a fake token (user id) for MVP
    return jsonify({'user_id': user.user_id, 'nickname': user.nickname, 'token': str(user.user_id)})


@app.route('/api/topics/apply', methods=['POST'])
def apply_topic():
    data = request.get_json() or {}
    title = data.get('title')
    description = data.get('description')
    side_pros = data.get('side_pros')
    side_cons = data.get('side_cons')
    rules = data.get('rules')
    is_public = data.get('is_public', True)
    created_by = data.get('created_by')
    if not (title and side_pros and side_cons and created_by):
        return jsonify({'error':'missing fields'}), 400
    topic = DebateTopic(title=title, description=description, side_pros=side_pros, side_cons=side_cons, rules=str(rules), is_public=is_public, status='pending', created_by=created_by)
    db.session.add(topic)
    db.session.commit()
    return jsonify({'topic_id': topic.topic_id, 'status': topic.status})


@app.route('/api/topics', methods=['GET'])
def list_topics():
    status = request.args.get('status')
    q = DebateTopic.query
    if status:
        q = q.filter_by(status=status)
    topics = q.all()
    out = []
    for t in topics:
        out.append({'topic_id': t.topic_id, 'title': t.title, 'status': t.status, 'created_by': t.created_by, 'created_at': t.created_at.isoformat() if t.created_at else None})
    return jsonify(out)


@app.route('/api/admin/topics/<int:topic_id>/approve', methods=['POST'])
def admin_approve(topic_id):
    t = DebateTopic.query.get_or_404(topic_id)
    t.status = 'approved'
    t.reviewed_by = request.json.get('admin_id')
    t.reviewed_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'topic_id': t.topic_id, 'status': t.status})


@app.route('/api/admin/topics/<int:topic_id>/reject', methods=['POST'])
def admin_reject(topic_id):
    t = DebateTopic.query.get_or_404(topic_id)
    t.status = 'rejected'
    t.reviewed_by = request.json.get('admin_id')
    t.reviewed_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'topic_id': t.topic_id, 'status': t.status})


@app.route('/api/debates/create', methods=['POST'])
def create_debate():
    data = request.get_json() or {}
    topic_id = data.get('topic_id')
    pros_user_id = data.get('pros_user_id')
    cons_user_id = data.get('cons_user_id')
    if not (topic_id and pros_user_id and cons_user_id):
        return jsonify({'error':'missing fields'}), 400
    debate = Debate(topic_id=topic_id, pros_user_id=pros_user_id, cons_user_id=cons_user_id, status='ongoing', round_count=0, created_at=datetime.utcnow())
    db.session.add(debate)
    db.session.commit()
    return jsonify({'debate_id': debate.debate_id, 'status': debate.status})


@app.route('/api/debates/<int:debate_id>', methods=['GET'])
def get_debate(debate_id):
    d = Debate.query.get_or_404(debate_id)
    return jsonify({'debate_id': d.debate_id, 'topic_id': d.topic_id, 'rounds_played': d.round_count, 'status': d.status, 'pros': {'user_id': d.pros_user_id}, 'cons': {'user_id': d.cons_user_id}})


@app.route('/api/debates/<int:debate_id>/rounds/create', methods=['POST'])
def create_round(debate_id):
    debate = Debate.query.get_or_404(debate_id)
    debate.round_count = (debate.round_count or 0) + 1
    rnd = Round(debate_id=debate_id, round_number=debate.round_count)
    db.session.add(rnd)
    db.session.commit()
    return jsonify({'round_id': rnd.round_id, 'round_number': rnd.round_number})


@app.route('/api/rounds/<int:round_id>/pros_statement', methods=['POST'])
def pros_statement(round_id):
    data = request.get_json() or {}
    content = data.get('content')
    rnd = Round.query.get_or_404(round_id)
    rnd.pros_statement = content
    db.session.commit()
    return jsonify({'round_id': rnd.round_id})


@app.route('/api/rounds/<int:round_id>/cons_questions', methods=['POST'])
def cons_questions(round_id):
    data = request.get_json() or {}
    questions = data.get('questions')
    rnd = Round.query.get_or_404(round_id)
    rnd.cons_questions = str(questions)
    db.session.commit()
    return jsonify({'round_id': rnd.round_id})


@app.route('/api/rounds/<int:round_id>/pros_reply', methods=['POST'])
def pros_reply(round_id):
    data = request.get_json() or {}
    content = data.get('content')
    rnd = Round.query.get_or_404(round_id)
    rnd.pros_reply = content
    db.session.commit()
    return jsonify({'round_id': rnd.round_id})


@app.route('/api/rounds/<int:round_id>/cons_statement', methods=['POST'])
def cons_statement(round_id):
    data = request.get_json() or {}
    content = data.get('content')
    rnd = Round.query.get_or_404(round_id)
    rnd.cons_statement = content
    db.session.commit()
    return jsonify({'round_id': rnd.round_id})


@app.route('/api/rounds/<int:round_id>/pros_questions', methods=['POST'])
def pros_questions(round_id):
    data = request.get_json() or {}
    questions = data.get('questions')
    rnd = Round.query.get_or_404(round_id)
    rnd.pros_questions = str(questions)
    db.session.commit()
    return jsonify({'round_id': rnd.round_id})


@app.route('/api/rounds/<int:round_id>/cons_reply', methods=['POST'])
def cons_reply(round_id):
    data = request.get_json() or {}
    content = data.get('content')
    rnd = Round.query.get_or_404(round_id)
    rnd.cons_reply = content
    db.session.commit()
    return jsonify({'round_id': rnd.round_id})


@app.route('/api/ranking', methods=['GET'])
def ranking():
    users = User.query.order_by(User.rating.desc()).limit(50).all()
    out = []
    for u in users:
        out.append({'user_id': u.user_id, 'nickname': u.nickname, 'rating': u.rating, 'wins': u.wins, 'losses': u.losses})
    return jsonify(out)


@app.route('/api/rounds/<int:round_id>/vote', methods=['POST'])
def vote(round_id):
    data = request.get_json() or {}
    side_voted = data.get('side_voted')
    is_judge = data.get('is_judge', False)
    voter_id = data.get('voter_id')
    if not (side_voted and voter_id):
        return jsonify({'error':'missing fields'}), 400
    # check unique vote
    existing = Vote.query.filter_by(round_id=round_id, voter_id=voter_id).first()
    if existing:
        return jsonify({'error':'already voted'}), 400
    weight = 10 if is_judge else 1
    v = Vote(round_id=round_id, voter_id=voter_id, side_voted=side_voted, is_judge=1 if is_judge else 0, weight=weight, created_at=datetime.utcnow())
    db.session.add(v)
    db.session.commit()
    return jsonify({'vote_id': v.vote_id})


@app.route('/api/rounds/<int:round_id>/results', methods=['GET'])
def round_results(round_id):
    res = compute_round_result(db, round_id)
    return jsonify(res)


@app.route('/static-sample')
def static_sample():
    return app.send_static_file('sample.txt')


if __name__ == '__main__':
    app.run(debug=True)
