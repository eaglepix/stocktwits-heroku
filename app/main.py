import gunicorn
from flask import Flask, render_template, abort, redirect, jsonify, request, make_response
from flask_cors import CORS
# from scrape_stocktwits_v1_4heroku import main
import json

from flask.helpers import url_for
from scrape_stocktwits_v1_4heroku import main_process

from google.oauth2 import service_account
from googleapiclient.discovery import build
from apiclient import errors

import os, asyncio

###################################################################################
local_gc_path = '../../googleDrive/client_secrets.json'

"""Getting Google Drive Credential and get the service module running"""
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# global SERVICE_ACCOUNT_FILE
SERVICE_ACCOUNT_FILE = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
API_NAME = 'drive'
API_VERSION = 'v3'
ctr2=10

if SERVICE_ACCOUNT_FILE == None:
    print('main.py SERVICE_ACCOUNT_FILE is NONE, look into local...', ctr2)
    ctr2*=2
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

#######################################################################
app = Flask(__name__, template_folder = os.path.join('../templates'), static_folder='../static')
cors = CORS(app, supports_credentials=True, resources={r"/*": {'origins':'https://drive.google.com'}})
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route("/", methods=["GET", "OPTIONS"])
# @cross_origin()
def welcome():
    origin = request.headers.get('Origin')
    if request.method == "OPTIONS": # CORS preflight
        response = make_response()
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', "Content-Type")
        response.headers.add('Access-Control-Allow-Headers', 'x-csrf-token')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, PATCH, DELETE')
        if origin:
            response.headers.add('Access-Control-Allow-Origin', origin)
    else:
        response = make_response()
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        if origin:
            response.headers.add('Access-Control-Allow-Origin', origin)

    return render_template("welcome.html")

@app.route('/execute/<id>')  #<client_id>
def startExecuting(id):
    if id == loginfile["client_id"]:
        return redirect(url_for('results', id_status='OK'))

    else: abort(404)

@app.route('/results/<id_status>')
def results(id_status):
    if id_status == 'OK':
        try:
            print('Running main_process now... please be patient')
            popularShort, popularMidTerm, popularPeriod = main_process()

            return render_template(
                "results.html",
                message='Stocktwits popular stocks:',
                popularPeriod = popularPeriod,
                table_popularity = [popularShort.to_html(classes='data', header='true')],
                table_trending = [popularMidTerm.to_html(classes='data', header='true')]
                )
        except:
            abort(404)
    else: abort(404)

