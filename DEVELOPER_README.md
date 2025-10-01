Debate Website MVP - Developer Notes

What this MVP includes
- Flask app with minimal API endpoints matching README spec (mock Line login)
- SQLite DB via SQLAlchemy models
- Elo calculation and simple round result processing

How to run (Windows PowerShell)

1. Activate the project's virtual environment (created by the tools):

   C:/Users/purem/Documents/辯論討論網站/.venv/Scripts/Activate.ps1

2. Install dependencies (already done by the helper):

   C:/Users/purem/Documents/辯論討論網站/.venv/Scripts/python.exe -m pip install -r requirements.txt

3. Initialize DB:

   C:/Users/purem/Documents/辯論討論網站/.venv/Scripts/python.exe db_init.py

4. Run the app:

   C:/Users/purem/Documents/辯論討論網站/.venv/Scripts/python.exe app.py

API notes
- Auth: POST /api/auth/login with {"line_id":"...","nickname":"..."} returns a fake token (user_id)
- Topics: POST /api/topics/apply, GET /api/topics
- Admin: POST /api/admin/topics/<id>/approve or /reject
- Debates: POST /api/debates/create, GET /api/debates/<id>
- Rounds: create with POST /api/debates/<id>/rounds/create
- Round actions: pros_statement, cons_questions, pros_reply, cons_statement, pros_questions, cons_reply
- Voting: POST /api/rounds/<id>/vote
- Results: GET /api/rounds/<id>/results
- Ranking: GET /api/ranking

Assumptions & limitations
- Line login is mocked for MVP
- Uses SQLite for simplicity; README described SQL Server
- No auth enforcement; token is a placeholder
- No migrations included beyond create_all
- Frontend is minimal

Next steps
- Add JWT and Line OAuth integration
- Switch to SQL Server and add migrations
- Add proper error handling and tests
