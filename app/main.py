import os
from flask import Flask, render_template, abort, flash, redirect, jsonify
# from scrape_stocktwits_v1_4heroku import main
import json

from flask.helpers import url_for
from scrape_stocktwits_v1_4heroku import SERVICE_ACCOUNT_FILE, main_process


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
        return redirect(url_for('/results'))

    else: abort(404)

@app.route('/results')
def results():
    try:
        popularity, trending = main_process()
        return render_template(
            "execute.html",
            message='Top 30 popular stocks:',
            popularity = popularity,
            trending = trending
            )
    except:
        abort(404)
