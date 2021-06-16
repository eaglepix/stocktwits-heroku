import os
from flask import Flask, render_template, abort, flash, redirect, jsonify
# from scrape_stocktwits_v1_4heroku import main
import json

from flask.helpers import url_for
from scrape_stocktwits_v1_4heroku import main_process

from google.oauth2 import service_account
from googleapiclient.discovery import build
# from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from apiclient import errors

import io, os
# import mimetypes
from requests.models import HTTPError

###################################################################################
local_gc_path = '../../googleDrive/client_secrets.json'

"""Getting Google Drive Credential and get the service module running"""
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# global SERVICE_ACCOUNT_FILE
SERVICE_ACCOUNT_FILE = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
API_NAME = 'drive'
API_VERSION = 'v3'

if SERVICE_ACCOUNT_FILE == None:
    print('SERVICE_ACCOUNT_FILE is NONE, look into local...')
    try:
        SERVICE_ACCOUNT_FILE = local_gc_path
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

@app.route("/")
def welcome():
    # return "Welcome page html"
    return render_template("welcome.html")

@app.route('/execute/<id>')  #/card/<int:index>
def startExecuting(id):
    with open(SERVICE_ACCOUNT_FILE) as f:
        loginfile = json.load(f)
        print(loginfile['client_id'])

    if id == loginfile["client_id"]:
        print('Running main_process now')
        # flash('Begin executing the main process... please be VERY patient')
        return redirect(url_for('results'))

    else: abort(404)

@app.route('/results')
def results():
    try:
        popularity, trending = main_process()
        return render_template(
            "results.html",
            message='Top 30 popular stocks:',
            popularity = popularity,
            trending = trending
            )
    except:
        abort(404)
