import gunicorn
from flask import Flask, render_template, abort, redirect, jsonify, request, make_response, flash, session
from flask_cors import CORS
# from scrape_stocktwits_v1_4heroku import main
import json

from flask.helpers import url_for
from requests.models import Response
from scrape_stocktwits_v1_4heroku import main_process

from google.oauth2 import service_account
from googleapiclient.discovery import build
from apiclient import errors

import os
import secrets
import concurrent.futures


###################################################################################
local_gc_path = '../../googleDrive/client_secrets.json'

"""Getting Google Drive Credential and get the service module running"""
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# global SERVICE_ACCOUNT_FILE
SERVICE_ACCOUNT_FILE = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
API_NAME = 'drive'
API_VERSION = 'v3'
ctr2 = 10
loginfile = ''

if SERVICE_ACCOUNT_FILE == None:
    print('main.py SERVICE_ACCOUNT_FILE is NONE, look into local...', ctr2)
    ctr2 *= 2
    try:
        SERVICE_ACCOUNT_FILE = local_gc_path
        with open(SERVICE_ACCOUNT_FILE) as f:
            loginfile = json.load(f)
    except:
        print('Error in retrieving Google Authentication file')
        os.abort()

# project name
gcp_project = os.environ.get('GCP_PROJECT')

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=credentials)

if loginfile == '':
    loginfile = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
#######################################################################
app = Flask(__name__, template_folder=os.path.join(
    '../templates'), static_folder='../static')
cors = CORS(app, supports_credentials=True, resources={
            r"/*": {'origins': 'https://drive.google.com'}})
app.config['CORS_HEADERS'] = 'Content-Type'

# Generate secret for the session
secret = secrets.token_urlsafe(32)
app.secret_key = secret

# def run_main_process():
#     global popularShort, popularMidTerm, popularPeriod
#     popularShort, popularMidTerm, popularPeriod = main_process()
#     return popularShort, popularMidTerm, popularPeriod


@app.route("/", methods=["GET", "OPTIONS"])
# @cross_origin()
def welcome():
    origin = request.headers.get('Origin')
    if request.method == "OPTIONS":  # CORS preflight
        response = make_response()
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', "Content-Type")
        response.headers.add('Access-Control-Allow-Headers', 'x-csrf-token')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, OPTIONS, PUT, PATCH, DELETE')
        if origin:
            response.headers.add('Access-Control-Allow-Origin', origin)
    else:
        response = make_response()
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        if origin:
            response.headers.add('Access-Control-Allow-Origin', origin)

    return render_template("welcome.html")


@app.route('/execute/<int:id>')  # <client_id>
def startExecuting(id):
    if id == int(loginfile["client_id"]):
        flash("Please WAIT for few minutes while we are processing the data ... ", "info")
        # response = Response(status=200)
        # status = '200 OK'
        # session['id_status'] = status
        return redirect(url_for('results'))
    else:
        abort(404)


@app.route('/processing/')
def processing():
    id_status = request.args['id_status']
    id_status = session['id_status']
    if id_status == id_status:
        flash("Please WAIT ... ", "info")
        # return render_template('wait.html')
        redirect(url_for('results'))
    else:
        abort(404)


@app.route('/processing')
def main_process_execution():
    try:
        print('Running main_process now... please be patient')
        global popularShort, popularMidTerm, popularPeriod
        popularShort, popularMidTerm, popularPeriod = main_process()
        return redirect(url_for('results', popularShort, popularMidTerm, popularPeriod))

    except:
        abort(404)


@app.route('/results/')
def results():  # id_status
    # if id_status == 'OK':
    # try:

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(main_process, )
        return_value = future.result()
        print(len(return_value))
    popularShort, popularMidTerm, popularPeriod = return_value

    return render_template(
        "results.html",
        message='Stocktwits popular stocks:',
        popularPeriod=popularPeriod,
        table_popularity=[popularShort.to_html(
            classes='data', header=True)],
        table_trending=[popularMidTerm.to_html(
            classes='data', header=True)]
    )
    # except:
    #     abort(404)
    # else:
    #     print('Status not OK!')
    #     abort(404)


"""
from flask import session, url_for

def do_baz():
    messages = json.dumps({"main":"Condition failed on page baz"})
    session['messages'] = messages
    return redirect(url_for('.do_foo', messages=messages))

@app.route('/foo')
def do_foo():
    messages = request.args['messages']  # counterpart for url_for()
    messages = session['messages']       # counterpart for session
    return render_template("foo.html", messages=json.loads(messages))
"""
