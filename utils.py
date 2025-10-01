from models import Vote, Debate, Round, MatchHistory, User
from sqlalchemy import func

def calculate_elo(rating_a, rating_b, score_a, score_b, k=32):
    expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    expected_b = 1 / (1 + 10 ** ((rating_a - rating_b) / 400))
    new_a = rating_a + k * (score_a - expected_a)
    new_b = rating_b + k * (score_b - expected_b)
    return round(new_a), round(new_b)


def compute_round_result(db, round_id):
    # sum weights by side
    pros_votes = db.session.query(func.sum(Vote.weight)).filter(Vote.round_id==round_id, Vote.side_voted=='pros').scalar() or 0
    cons_votes = db.session.query(func.sum(Vote.weight)).filter(Vote.round_id==round_id, Vote.side_voted=='cons').scalar() or 0
    total = pros_votes + cons_votes
    if total == 0:
        pros_pct = cons_pct = 0
    else:
        pros_pct = pros_votes * 100.0 / total
        cons_pct = cons_votes * 100.0 / total

    # find debate and players
    rnd = Round.query.get(round_id)
    debate = Debate.query.get(rnd.debate_id)
    pros_user = User.query.get(debate.pros_user_id)
    cons_user = User.query.get(debate.cons_user_id)

    winner = None
    if pros_pct >= 70:
        winner = 'pros'
    elif cons_pct >= 70:
        winner = 'cons'

    result = {
        'pros_votes': int(pros_votes),
        'cons_votes': int(cons_votes),
        'pros_percentage': pros_pct,
        'cons_percentage': cons_pct,
        'winner': winner
    }

    # If winner, update debate and match history and Elo
    if winner:
        if winner == 'pros':
            winner_id = pros_user.user_id
            loser_id = cons_user.user_id
            score_winner = 1
            score_loser = 0
        else:
            winner_id = cons_user.user_id
            loser_id = pros_user.user_id
            score_winner = 1
            score_loser = 0

        # record match history and update ratings
        rating_w_before = User.query.get(winner_id).rating
        rating_l_before = User.query.get(loser_id).rating
        new_w, new_l = calculate_elo(rating_w_before, rating_l_before, score_winner, score_loser)

        mh_win = MatchHistory(debate_id=debate.debate_id, user_id=winner_id, result='win', rating_before=rating_w_before, rating_after=new_w)
        mh_loss = MatchHistory(debate_id=debate.debate_id, user_id=loser_id, result='loss', rating_before=rating_l_before, rating_after=new_l)
        db.session.add(mh_win)
        db.session.add(mh_loss)

        # update user ratings and wins/losses
        uw = User.query.get(winner_id)
        ul = User.query.get(loser_id)
        uw.rating = new_w
        ul.rating = new_l
        uw.wins = (uw.wins or 0) + 1
        ul.losses = (ul.losses or 0) + 1

        # finalize debate
        debate.status = 'finished'
        debate.winner_id = winner_id
        debate.finished_at = func.now()
        rnd.status = 'completed'
        db.session.commit()

        result['winner_id'] = winner_id
        result['rating_winner_after'] = new_w
        result['rating_loser_after'] = new_l

    else:
        # mark round completed but debate continues
        rnd.status = 'completed'
        db.session.commit()

    return result
