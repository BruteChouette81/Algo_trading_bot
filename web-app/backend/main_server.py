import flask
from flask import request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///registration.db'
db = SQLAlchemy(app)
user_create = {"resp": 200}
bad_request = {"resp": 401}

class User(db.Model):
    id = db.Column(db.Integer, primary_key =True)
    username = db.Column(db.String(100), nullable = False)
    user_password = db.Column(db.String(150), nullable = False)


@app.route('/create_account', methods=['POST'])
def create_account():
    input_json = request.get_json(force=True) 
    user = User(username = input_json["user"], user_password = input_json["password"])
        
    # add the user object to the database
    db.session.add(user)
        
     # commit changes to the database 
    db.session.commit()
    return jsonify(user_create)


@app.route('/log_account', methods=['POST'])
def log_account():
    input_json = request.get_json(force=True)
    print(str(input_json["user"]))
    user_data = User.query.all()
    for user in user_data:
        print(user)
        if input_json["user"] == user.username:
            if input_json["password"] == user.password:
                return jsonify({"user": user.username, "code": 201})

            else:
                return jsonify({"info": "password incorrect"}) 
        else:
            return jsonify({"info": "no account"}) 
app.run()