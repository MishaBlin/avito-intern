# api/auth.py
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from .extensions import db
from .models import User

auth = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth.route('', methods=['POST'])
def authenticate():
    data = request.get_json()
    if not data or "username" not in data or "password" not in data:
        return jsonify({"errors": "Username and password are required."}), 400

    username = data["username"]
    password = data["password"]

    user = User.query.filter_by(username=username).first()
    if user:
        if not check_password_hash(user.password, password):
            return jsonify({"errors": "Invalid username or password."}), 401
    else:
        hashed_password = generate_password_hash(password)
        user = User(username=username, password=hashed_password, balance=1000)
        db.session.add(user)
        db.session.commit()

    token = create_access_token(identity=user.username)
    return jsonify({"token": token}), 200
