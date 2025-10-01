import os
from flask import Blueprint, current_app, redirect, request, url_for, render_template
import requests
import jwt
from datetime import datetime, timedelta
from extensions import db
from models import User

bp = Blueprint('auth', __name__)

LINE_AUTH_URL = 'https://access.line.me/oauth2/v2.1/authorize'
LINE_TOKEN_URL = 'https://api.line.me/oauth2/v2.1/token'
LINE_PROFILE_URL = 'https://api.line.me/v2/profile'


def _get_conf(name, default=None):
    return os.environ.get(name, current_app.config.get(name, default))


@bp.route('/auth/line')
def line_login():
    client_id = _get_conf('LINE_CLIENT_ID')
    redirect_uri = _get_conf('LINE_REDIRECT_URI', url_for('auth.line_callback', _external=True))
    state = 'state123'  # for MVP; production should generate and validate per-session
    scope = 'profile openid'
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'state': state,
        'scope': scope,
    }
    url = LINE_AUTH_URL + '?' + '&'.join([f'{k}={requests.utils.requote_uri(v)}' for k,v in params.items()])
    return redirect(url)


@bp.route('/auth/line/callback')
def line_callback():
    code = request.args.get('code')
    if not code:
        return 'No code', 400

    client_id = _get_conf('LINE_CLIENT_ID')
    client_secret = _get_conf('LINE_CLIENT_SECRET')
    redirect_uri = _get_conf('LINE_REDIRECT_URI', url_for('auth.line_callback', _external=True))

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret,
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    token_resp = requests.post(LINE_TOKEN_URL, data=data, headers=headers)
    if token_resp.status_code != 200:
        return f'Token exchange failed: {token_resp.text}', 400
    token_json = token_resp.json()
    access_token = token_json.get('access_token')
    if not access_token:
        return 'No access token', 400

    # fetch profile
    prof_headers = {'Authorization': f'Bearer {access_token}'}
    prof_resp = requests.get(LINE_PROFILE_URL, headers=prof_headers)
    if prof_resp.status_code != 200:
        return f'Profile fetch failed: {prof_resp.text}', 400
    profile = prof_resp.json()
    # profile keys: userId, displayName, pictureUrl, statusMessage
    line_id = profile.get('userId')
    nickname = profile.get('displayName')
    avatar = profile.get('pictureUrl')

    # upsert user
    user = User.query.filter_by(line_id=line_id).first()
    if not user:
        user = User(line_id=line_id, nickname=nickname or 'LineUser', avatar=avatar)
        db.session.add(user)
        db.session.commit()
    else:
        # update profile info
        user.nickname = nickname or user.nickname
        user.avatar = avatar or user.avatar
        db.session.commit()

    # issue JWT
    jwt_secret = _get_conf('JWT_SECRET', 'dev-jwt-secret')
    payload = {
        'user_id': user.user_id,
        'nickname': user.nickname,
        'is_admin': bool(user.is_admin),
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    token = jwt.encode(payload, jwt_secret, algorithm='HS256')

    # render a small page that stores token to localStorage and redirects to home
    return render_template('token_redirect.html', token=token)
