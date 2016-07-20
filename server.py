import configparser

import requests
from flask import (
    Flask,
    jsonify,
    request,
)
app = Flask(__name__)
config = configparser.ConfigParser()
config.read('config.ini')

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/auth')
def oauth_callback():
    if request.args.get('error'):
        return 'Error: denied auth', 401
    code = request.args.get('code')
    if not code:
        return 'Error: missing code parameter', 400

    payload = {
        'client_id': config['Instagram']['ClientId'],
        'client_secret': config['Instagram']['ClientSecret'],
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': config['Server']['Hostname'] + "/auth",
    }

    r = requests.post(
        'https://api.instagram.com/oauth/access_token',
        data=payload
    )

    return jsonify(**r.json())
