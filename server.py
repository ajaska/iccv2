import configparser

import requests
from flask import (
    Flask,
    jsonify,
    redirect,
    request,
    session,
    url_for,
)
app = Flask(__name__)

config = configparser.ConfigParser()
config.read('config.ini')

app.secret_key = config['Server']['SecretKey']

ig_client_id = config['Instagram']['ClientId']
ig_client_secret = config['Instagram']['ClientSecret']
redirect_uri = 'http://' + config['Server']['Hostname'] + '/auth'

@app.route('/')
def index():
    return 'Hello, World!'

@app.route('/auth-redirect')
def oauth_redirect():
    redirect_url = (
        'https://api.instagram.com/oauth/authorize/?'
        'client_id={}&'
        'redirect_uri={}&'
        'response_type=code'
    ).format(ig_client_id, redirect_uri)
    return redirect(redirect_url, code=302)

@app.route('/auth')
def oauth_callback():
    if request.args.get('error'):
        return 'Error: denied auth', 401
    code = request.args.get('code')
    if not code:
        return 'Error: missing code parameter', 400

    payload = {
        'client_id': ig_client_id,
        'client_secret': ig_client_secret,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
    }

    r = requests.post(
        'https://api.instagram.com/oauth/access_token',
        data=payload
    )

    if r.status_code != 200:
        return jsonify(**r.json()), r.status_code

    data = r.json()
    session['access_token'] = data.get('access_token')
    return redirect(url_for('index'))
