from extensions import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'Users'
    user_id = db.Column(db.Integer, primary_key=True)
    line_id = db.Column(db.String(100), unique=True, nullable=False)
    nickname = db.Column(db.String(50), nullable=False)
    avatar = db.Column(db.String(255))
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    rating = db.Column(db.Integer, default=1500)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    is_admin = db.Column(db.Boolean, default=False)


class DebateTopic(db.Model):
    __tablename__ = 'DebateTopics'
    topic_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    side_pros = db.Column(db.String(500), nullable=False)
    side_cons = db.Column(db.String(500), nullable=False)
    rules = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='pending')
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_by = db.Column(db.Integer, nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)


class Debate(db.Model):
    __tablename__ = 'Debates'
    debate_id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, nullable=False)
    pros_user_id = db.Column(db.Integer, nullable=False)
    cons_user_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='ongoing')
    round_count = db.Column(db.Integer, default=0)
    winner_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime, nullable=True)


class Round(db.Model):
    __tablename__ = 'Rounds'
    round_id = db.Column(db.Integer, primary_key=True)
    debate_id = db.Column(db.Integer, nullable=False)
    round_number = db.Column(db.Integer, nullable=False)
    pros_statement = db.Column(db.Text)
    cons_questions = db.Column(db.Text)
    pros_reply = db.Column(db.Text)
    cons_statement = db.Column(db.Text)
    pros_questions = db.Column(db.Text)
    cons_reply = db.Column(db.Text)
    status = db.Column(db.String(20), default='in_progress')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Vote(db.Model):
    __tablename__ = 'Votes'
    vote_id = db.Column(db.Integer, primary_key=True)
    round_id = db.Column(db.Integer, nullable=False)
    voter_id = db.Column(db.Integer, nullable=False)
    side_voted = db.Column(db.String(10), nullable=False)
    is_judge = db.Column(db.Boolean, default=False)
    weight = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class JudgeAssignment(db.Model):
    __tablename__ = 'JudgeAssignments'
    judge_id = db.Column(db.Integer, primary_key=True)
    debate_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)


class MatchHistory(db.Model):
    __tablename__ = 'MatchHistory'
    match_id = db.Column(db.Integer, primary_key=True)
    debate_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    result = db.Column(db.String(10), nullable=False)
    rating_before = db.Column(db.Integer, nullable=False)
    rating_after = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
