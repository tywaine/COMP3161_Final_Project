from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import Config

from app.routes.auth import auth_bp
from app.routes.courses import courses_bp
from app.routes.calendarEvents import calendar_bp
from app.routes.forums import forums_bp
from app.routes.discussionThreads import threads_bp

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.json.sort_keys = False
    app.config.from_object(Config)

    CORS(app)
    jwt.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(forums_bp)
    app.register_blueprint(threads_bp)

    return app