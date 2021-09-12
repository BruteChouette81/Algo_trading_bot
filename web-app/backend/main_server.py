import flask
from flask import request, jsonify

app = flask.Flask(__name__)
app.config["DEBUG"] = True
user_data = {}


@app.route('/handle_account', methods=['POST'])
def home():
    input_json = request.get_json(force=True) 
    user_data = {"user": input_json["user"], "pass": input_json["password"]}
    print(user_data)
    return jsonify(user_data)

app.run()