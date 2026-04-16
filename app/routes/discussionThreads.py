from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from mysql.connector import Error

from app.db import get_db, close_db
from app.utils.response import error_response, success_response

threads_bp = Blueprint("threads", __name__, url_prefix="/api/threads")


@threads_bp.route("/create", methods=["POST"])
def create_thread():
    connection = None
    cursor = None

    try:
        data = request.get_json()

        forum_id = data.get("forumId")
        user_id = data.get("userId")
        title = data.get("title")
        content = data.get("content")

        if not forum_id or not user_id or not title:
            return error_response("Missing required fields")

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            INSERT INTO threads (forum_id, user_id, title, content)
            VALUES (%s, %s, %s, %s)
        """, (forum_id, user_id, title, content))

        connection.commit()

        return success_response("Thread created")

    except Error as e:
        return error_response("Database error", 500, e)

    finally:
        close_db(connection, cursor)