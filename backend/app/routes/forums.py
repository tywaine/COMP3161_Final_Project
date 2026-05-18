from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from mysql.connector import Error

from app.db import get_db, close_db
from app.utils.response import error_response, success_response
from datetime import datetime
from decimal import Decimal

forums_bp = Blueprint("forums", __name__, url_prefix="/api/forums")

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


@forums_bp.route("/course/<string:course_code>", methods=["GET"])
@jwt_required()
def get_forums_for_course(course_code: str):
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
            return error_response("You are not allowed to view forums for this course", 403)

        cursor.execute(
            """
            SELECT f.forumId,
                   f.courseCode,
                   f.title,
                   f.createdByUserId,
                   u.fullName AS createdByName,
                   f.createdAt
            FROM Forums f
                     JOIN Users u ON f.createdByUserId = u.userId
            WHERE f.courseCode = %s
            ORDER BY f.createdAt DESC
            """,
            (course_code,)
        )

        forums = cursor.fetchall()
        forums = [format_db_row(forum) for forum in forums]
        course = format_db_row(course)

        return success_response(
            "Forums retrieved successfully",
            {
                "course": course,
                "forums": forums
            }
        )


    except Error as e:
        print("DATABASE ERROR:", e)
        return error_response("Database error", 500, str(e))


    except Exception as e:
        print("SERVER ERROR:", e)
        return error_response("Server error", 500, str(e))

    finally:
        close_db(connection, cursor)


@forums_bp.route("/course/<string:course_code>", methods=["POST"])
@jwt_required()
def create_forum(course_code: str):
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
        if not title:
            return error_response("title is required")

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
            return error_response("You are not allowed to create a forum for this course", 403)

        cursor.execute(
            """
            INSERT INTO Forums (courseCode, title, createdByUserId)
            VALUES (%s, %s, %s)
            """,
            (course_code, title, current_user_id)
        )

        forum_id = cursor.lastrowid
        connection.commit()

        return success_response(
            "Forum created successfully",
            {
                "forum": {
                    "forumId": forum_id,
                    "courseCode": course_code,
                    "title": title,
                    "createdByUserId": current_user_id
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