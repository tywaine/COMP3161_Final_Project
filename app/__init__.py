from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import Config

from app.routes.auth import auth_bp

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    jwt.init_app(app)

    app.register_blueprint(auth_bp)

    return app