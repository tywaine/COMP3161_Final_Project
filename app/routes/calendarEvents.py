from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt
from mysql.connector import Error
from datetime import datetime

from app.db import get_db, close_db
from app.utils.response import error_response, success_response

calendar_bp = Blueprint("calendar", __name__, url_prefix="/api/calendar")


@calendar_bp.route("/create", methods=["POST"])
def create_event():
    connection = None
    cursor = None

    try:
        data = request.get_json()

        course_id = data.get("courseId")
        title = data.get("title")
        event_date = data.get("date")

        if not course_id or not title or not event_date:
            return error_response("Missing fields")

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            INSERT INTO calendar_events (course_id, title, event_date)
            VALUES (%s, %s, %s)
        """, (course_id, title, event_date))

        connection.commit()

        return success_response("Event created")

    except Error as e:
        return error_response("Database error", 500, e)

    finally:
        close_db(connection, cursor)