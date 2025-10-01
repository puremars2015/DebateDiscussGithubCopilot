from app import app, db
from models import User, DebateTopic, Debate, Round, Vote, MatchHistory

def init_db():
    with app.app_context():
        db.create_all()
        print('Database initialized.')

if __name__ == '__main__':
    init_db()
