import os
import requests
import json
from urllib.parse import urljoin

BASE = 'http://127.0.0.1:5000'

def main():
    # This script expects the app to be running locally.
    # Create a mock user via API
    login_payload = {'line_id':'test-admin-line','nickname':'TestAdmin'}
    r = requests.post(urljoin(BASE, '/api/auth/login'), json=login_payload)
    print('login:', r.status_code, r.text)
    user = r.json()
    uid = user.get('user_id')

    # Promote via admin endpoint using ADMIN_SECRET from env
    admin_secret = os.environ.get('ADMIN_SECRET')
    if not admin_secret:
        print('Please set ADMIN_SECRET environment variable before running this test script.')
        return
    promote_payload = {'user_id': uid}
    headers = {'X-ADMIN-SECRET': admin_secret}
    r2 = requests.post(urljoin(BASE, '/api/admin/promote'), json=promote_payload, headers=headers)
    print('promote:', r2.status_code, r2.text)

if __name__ == '__main__':
    main()
