from datetime import datetime
from decimal import Decimal
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from mysql.connector import Error

from app.db import get_db, close_db
from app.utils.response import error_response, success_response

calendar_events_bp = Blueprint(
    "calendar_events",
    __name__,
    url_prefix="/api/calendar-events"
)

def format_db_row(row):
    """Helper to convert database row values to JSON-serializable formats."""
    if not row:
        return row
    for key, value in row.items():
        if isinstance(value, datetime):
            row[key] = value.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(value, Decimal):
            row[key] = float(value)
    return row

def is_course_member(cursor, user_id, role, course_code):
    if role == "admin":
        return True

    if role == "lecturer":
        cursor.execute(
            """
            SELECT lecturerId
            FROM Teaching
            WHERE lecturerId = %s AND courseCode = %s
            """,
            (user_id, course_code)
        )
        return cursor.fetchone() is not None

    if role == "student":
        cursor.execute(
            """
            SELECT studentId
            FROM Enrollment
            WHERE studentId = %s AND courseCode = %s
            """,
            (user_id, course_code)
        )
        return cursor.fetchone() is not None

    return False


@calendar_events_bp.route("/course/<string:course_code>", methods=["GET"])
@jwt_required()
def get_calendar_events_for_course(course_code: str):
    connection = None
    cursor = None

    try:
        claims = get_jwt()
        current_role = claims.get("role")
        current_user_id = int(get_jwt_identity())
        course_code = course_code.upper().strip()

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT courseCode, courseName
            FROM Courses
            WHERE courseCode = %s
            """,
            (course_code,)
        )
        course = cursor.fetchone()

        if not course:
            return error_response("Course not found", 404)

        if not is_course_member(cursor, current_user_id, current_role, course_code):
            return error_response("You are not allowed to view calendar events for this course", 403)

        cursor.execute(
            """
            SELECT ce.eventId,
                   ce.courseCode,
                   ce.createdByUserId,
                   u.fullName AS createdByName,
                   ce.title,
                   ce.description,
                   ce.eventDateTime,
                   ce.createdAt
            FROM CalendarEvents ce
                     JOIN Users u ON ce.createdByUserId = u.userId
            WHERE ce.courseCode = %s
            ORDER BY ce.eventDateTime
            """,
            (course_code,)
        )
        events = [format_db_row(row) for row in cursor.fetchall()]

        return success_response(
            "Calendar events retrieved successfully",
            {
                "course": format_db_row(course),
                "events": events
            }
        )

    except Error as e:
        return error_response("Database error", 500, e)

    except Exception as e:
        return error_response("Server error", 500, e)

    finally:
        close_db(connection, cursor)


@calendar_events_bp.route("/student/<int:student_id>", methods=["GET"])
@jwt_required()
def get_calendar_events_for_student_by_date(student_id):
    connection = None
    cursor = None

    try:
        claims = get_jwt()
        current_role = claims.get("role")
        current_user_id = int(get_jwt_identity())

        if current_role == "student" and current_user_id != student_id:
            return error_response("Students can only view their own events", 403)

        date_value = request.args.get("date")
        if not date_value:
            return error_response("date query parameter is required in YYYY-MM-DD format")

        try:
            datetime.strptime(date_value, "%Y-%m-%d")
        except ValueError:
            return error_response("date must be in YYYY-MM-DD format")

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT userId FROM Students WHERE userId = %s",
            (student_id,)
        )
        student = cursor.fetchone()

        if not student:
            return error_response("Student not found", 404)

        cursor.execute(
            """
            SELECT ce.eventId,
                   ce.courseCode,
                   c.courseName,
                   ce.createdByUserId,
                   u.fullName AS createdByName,
                   ce.title,
                   ce.description,
                   ce.eventDateTime,
                   ce.createdAt
            FROM Enrollment e
                     JOIN CalendarEvents ce ON e.courseCode = ce.courseCode
                     JOIN Courses c ON ce.courseCode = c.courseCode
                     JOIN Users u ON ce.createdByUserId = u.userId
            WHERE e.studentId = %s
              AND DATE(ce.eventDateTime) = %s
            ORDER BY ce.eventDateTime
            """,
            (student_id, date_value)
        )
        events = [format_db_row(row) for row in cursor.fetchall()]

        return success_response(
            "Student calendar events retrieved successfully",
            {
                "studentId": student_id,
                "date": date_value,
                "events": events
            }
        )

    except Error as e:
        return error_response("Database error", 500, e)

    except Exception as e:
        return error_response("Server error", 500, e)

    finally:
        close_db(connection, cursor)


@calendar_events_bp.route("/course/<string:course_code>", methods=["POST"])
@jwt_required()
def create_calendar_event(course_code: str):
    connection = None
    cursor = None

    try:
        claims = get_jwt()
        current_role = claims.get("role")
        current_user_id = int(get_jwt_identity())
        course_code = course_code.upper().strip()

        data = request.get_json()
        if not data:
            return error_response("Request body must be JSON")

        title = data.get("title")
        description = data.get("description")
        event_date_time = data.get("eventDateTime")

        if not title or not event_date_time:
            return error_response("title and eventDateTime are required")

        try:
            parsed_event_date_time = datetime.strptime(event_date_time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return error_response("eventDateTime must be in YYYY-MM-DD HH:MM:SS format")

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT courseCode, courseName
            FROM Courses
            WHERE courseCode = %s
            """,
            (course_code,)
        )
        course = cursor.fetchone()

        if not course:
            return error_response("Course not found", 404)

        allowed = False

        if current_role == "admin":
            allowed = True
        elif current_role == "lecturer":
            cursor.execute(
                """
                SELECT lecturerId
                FROM Teaching
                WHERE lecturerId = %s AND courseCode = %s
                """,
                (current_user_id, course_code)
            )
            allowed = cursor.fetchone() is not None

        if not allowed:
            return error_response("Only an admin or the assigned lecturer can create calendar events", 403)

        cursor.execute(
            """
            INSERT INTO CalendarEvents (courseCode, createdByUserId, title, description, eventDateTime)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                course_code,
                current_user_id,
                title,
                description,
                parsed_event_date_time
            )
        )

        event_id = cursor.lastrowid
        connection.commit()

        return success_response(
            "Calendar event created successfully",
            {
                "event": {
                    "eventId": event_id,
                    "courseCode": course_code,
                    "createdByUserId": current_user_id,
                    "title": title,
                    "description": description,
                    "eventDateTime": event_date_time
                }
            },
            201
        )

    except Error as e:
        return error_response("Database error", 500, e)

    except Exception as e:
        return error_response("Server error", 500, e)

    finally:
        close_db(connection, cursor)


@calendar_events_bp.route("/upcoming", methods=["GET"])
@jwt_required()
def get_upcoming_events():
    connection = None
    cursor = None
    try:
        claims = get_jwt()
        current_role = claims.get("role")
        current_user_id = int(get_jwt_identity())
        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        if current_role == "admin":
            query = """
                SELECT ce.eventId, ce.title, ce.eventDateTime, c.courseCode
                FROM CalendarEvents ce
                JOIN Courses c ON ce.courseCode = c.courseCode
                WHERE ce.eventDateTime >= NOW()
                ORDER BY ce.eventDateTime
                LIMIT 5
            """
            cursor.execute(query)
        elif current_role == "student":
            query = """
                SELECT ce.eventId, ce.title, ce.eventDateTime, c.courseCode
                FROM Enrollment e
                JOIN CalendarEvents ce ON e.courseCode = ce.courseCode
                JOIN Courses c ON ce.courseCode = c.courseCode
                WHERE e.studentId = %s AND ce.eventDateTime >= NOW()
                ORDER BY ce.eventDateTime
                LIMIT 5
            """
            cursor.execute(query, (current_user_id,))
        else: # Lecturer
            query = """
                SELECT ce.eventId, ce.title, ce.eventDateTime, c.courseCode
                FROM Teaching t
                JOIN CalendarEvents ce ON t.courseCode = ce.courseCode
                JOIN Courses c ON ce.courseCode = c.courseCode
                WHERE t.lecturerId = %s AND ce.eventDateTime >= NOW()
                ORDER BY ce.eventDateTime
                LIMIT 5
            """
            cursor.execute(query, (current_user_id,))

        events = [format_db_row(row) for row in cursor.fetchall()]
        return success_response("Upcoming events retrieved", {"events": events})
    except Error as e:
        return error_response("Database error", 500, e)
    except Exception as e:
        return error_response("Server error", 500, e)
    finally:
        close_db(connection, cursor)