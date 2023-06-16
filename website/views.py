from flask import Blueprint, render_template ,jsonify,request
import os,sys,requests, json
from flask_login import login_required, current_user
from random import randint


views = Blueprint("views", __name__)


@views.route("/")
@views.route("/home")
#@login_required
def home():
    return render_template("home.html")


@views.route('/chat')
def chat():
    return render_template('chat.html')

@views.route('/processchat', methods=['GET','POST'])
@login_required
def process_chat():
    text = request.args.get('text')
    payload = json.dumps({"sender": "Rasa", "message": text})
    headers = {'Content-type': 'application/json'}
    response = requests.post("http://localhost:5005/webhooks/rest/webhook", headers=headers, data=payload)
    response_data = response.json()
    resp = response_data[0]["text"]
  
    return jsonify(resp)

