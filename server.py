import configparser
from collections import namedtuple

import requests
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
app = Flask(__name__)

config = configparser.ConfigParser()
config.read('config.ini')

ig_client_id = config['Instagram']['ClientId']
ig_client_secret = config['Instagram']['ClientSecret']

redirect_uri = config['Server']['BaseUri'] + '/auth'
app.secret_key = config['Server']['SecretKey']

Image = namedtuple('Image', ['location', 'image'])


def select_properties(media):
    return Image(
        media['location'],
        media['images']['standard_resolution']['url']
    )


@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))


@app.route('/')
def index():
    access_token = session.get('access_token')
    if not access_token:
        return render_template('index.html')
    payload = {'access_token': access_token}
    r = requests.get(
        "https://api.instagram.com/v1/tags/icecreamcollective/media/recent",
        params=payload
    )
    data = r.json().get("data")
    if data is None:
        return render_template(
            'index.html',
            error="Error: " + r.text
        ), 500
    elif not data:
        return render_template(
            'index.html',
            error="Error: found no ice cream images :("
        ), 500

    data = filter(lambda media: media.get('location') is not None, data)
    data = filter(lambda media: media.get('type') == 'image', data)
    data = map(select_properties, data)
    data = list(data)
    if not data:
        return render_template(
            'index.html',
            error="There is no ice cream :("
        ), 404
    return render_template(
        'map.html',
        gmaps_api_key=config['Google Maps']['ApiKey'],
        images=data
    )


@app.route('/auth-redirect')
def oauth_redirect():
    redirect_url = (
        'https://api.instagram.com/oauth/authorize/?'
        'client_id={}&'
        'redirect_uri={}&'
        'scope=basic+public_content&'
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
