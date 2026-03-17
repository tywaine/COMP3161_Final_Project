from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import Config

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    jwt.init_app(app)

    """

    """

    return app