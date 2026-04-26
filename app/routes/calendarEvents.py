from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from mysql.connector import Error
from datetime import datetime

from app.db import get_db, close_db
from app.utils.response import error_response, success_response

calendar_bp = Blueprint("calendar", __name__, url_prefix="/api/calendar")

@calendar_bp.route("/course/<int:course_id>", methods=["GET"])
@jwt_required()
def get_course_events(course_id):
    connection = None
    cursor = None
    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT eventId, courseId, createdByUserId, title, description, eventDateTime, createdAt
            FROM CalendarEvents
            WHERE courseId = %s
            ORDER BY eventDateTime ASC
        """, (course_id,))
        events = cursor.fetchall()

        return success_response("Events retrieved successfully", {"events": events})
    except Error as e:
        return error_response("Database error", 500, e)
    finally:
        close_db(connection, cursor)


@calendar_bp.route("/student/<int:student_id>/date/<date_string>", methods=["GET"])
@jwt_required()
def get_student_events_by_date(student_id, date_string):
    connection = None
    cursor = None
    try:
        # Validate date string format (YYYY-MM-DD)
        try:
            datetime.strptime(date_string, "%Y-%m-%d")
        except ValueError:
            return error_response("Invalid date format. Use YYYY-MM-DD", 400)

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT c.eventId, c.courseId, c.createdByUserId, c.title, c.description, c.eventDateTime, c.createdAt
            FROM CalendarEvents c
            JOIN Enrollment e ON c.courseId = e.courseId
            WHERE e.studentId = %s AND DATE(c.eventDateTime) = %s
            ORDER BY c.eventDateTime ASC
        """
        cursor.execute(query, (student_id, date_string))
        events = cursor.fetchall()

        return success_response("Events retrieved successfully", {"events": events})
    except Error as e:
        return error_response("Database error", 500, e)
    finally:
        close_db(connection, cursor)


@calendar_bp.route("/course/<int:course_id>", methods=["POST"])
@jwt_required()
def create_event(course_id):
    connection = None
    cursor = None
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return error_response("Request body must be JSON")

        title = data.get("title")
        description = data.get("description")
        event_datetime = data.get("eventDateTime")

        if not title or not event_datetime:
            return error_response("title and eventDateTime are required", 400)

        # Validate datetime format (YYYY-MM-DD HH:MM:SS)
        try:
            datetime.strptime(event_datetime, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return error_response("Invalid eventDateTime format. Use YYYY-MM-DD HH:MM:SS", 400)

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        # Check if course exists
        cursor.execute("SELECT courseId FROM Courses WHERE courseId = %s", (course_id,))
        if not cursor.fetchone():
            return error_response("Course not found", 404)

        insert_sql = """
            INSERT INTO CalendarEvents (courseId, createdByUserId, title, description, eventDateTime)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_sql, (course_id, user_id, title, description, event_datetime))
        connection.commit()

        event_id = cursor.lastrowid

        return success_response(
            "Event created successfully",
            {
                "event": {
                    "eventId": event_id,
                    "courseId": course_id,
                    "createdByUserId": int(user_id),
                    "title": title,
                    "description": description,
                    "eventDateTime": event_datetime
                }
            },
            201
        )
    except Error as e:
        if connection:
            connection.rollback()
        return error_response("Database error", 500, e)
    finally:
        close_db(connection, cursor)