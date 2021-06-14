import os
from flask import Flask, render_template, abort, jsonify
# from scrape_stocktwits_v1_4heroku import main

app = Flask(__name__)

@app.route("/")
def welcome():
    # return "Welcome page html"
    return render_template("welcome.html")

@app.route('/execute')  #/card/<int:index>
def startExecuting():
    try:
        # main()
        return render_template(
            "execute.html",
            message='Injected message from py script')
    except:
        abort(404)
