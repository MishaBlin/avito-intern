import os
from flask import Flask, current_app
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from .extensions import db
from .storage import init_db
from .auth import auth
from .routes import main

load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
JWT_SECRET = os.getenv('JWT_SECRET_KEY')


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = \
        f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = JWT_SECRET

    # Initialize extensions
    db.init_app(app)
    JWTManager(app)

    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(main)

    # Initialize and seed the database
    init_db(app)

    return app
