from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from mysql.connector import Error

from app.db import get_db, close_db
from app.utils.response import error_response, success_response

forums_bp = Blueprint("forums", __name__, url_prefix="/api/forums")


def is_course_member(cursor, user_id, role, course_id):
    if role == "admin":
        return True

    if role == "lecturer":
        cursor.execute(
            """
            SELECT lecturerId
            FROM Teaching
            WHERE lecturerId = %s AND courseId = %s
            """,
            (user_id, course_id)
        )
        return cursor.fetchone() is not None

    if role == "student":
        cursor.execute(
            """
            SELECT studentId
            FROM Enrollment
            WHERE studentId = %s AND courseId = %s
            """,
            (user_id, course_id)
        )
        return cursor.fetchone() is not None

    return False


@forums_bp.route("/course/<int:course_id>", methods=["GET"])
@jwt_required()
def get_forums_for_course(course_id: int):
    connection = None
    cursor = None

    try:
        claims = get_jwt()
        current_role = claims.get("role")
        current_user_id = int(get_jwt_identity())

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT courseId, courseCode, courseName
            FROM Courses
            WHERE courseId = %s
            """,
            (course_id,)
        )
        course = cursor.fetchone()

        if not course:
            return error_response("Course not found", 404)

        if not is_course_member(cursor, current_user_id, current_role, course_id):
            return error_response("You are not allowed to view forums for this course", 403)

        cursor.execute(
            """
            SELECT
                f.forumId,
                f.courseId,
                f.title,
                f.createdByUserId,
                u.fullName AS createdByName,
                DATE_FORMAT(f.createdAt, '%Y-%m-%d %H:%i:%s') AS createdAt
            FROM Forums f
            JOIN Users u ON f.createdByUserId = u.userId
            WHERE f.courseId = %s
            ORDER BY f.createdAt DESC
            """,
            (course_id,)
        )
        forums = cursor.fetchall()

        return success_response(
            "Forums retrieved successfully",
            {
                "course": course,
                "forums": forums
            }
        )

    except Error as e:
        return error_response("Database error", 500, e)

    except Exception as e:
        return error_response("Server error", 500, e)

    finally:
        close_db(connection, cursor)


@forums_bp.route("/course/<int:course_id>", methods=["POST"])
@jwt_required()
def create_forum(course_id: int):
    connection = None
    cursor = None

    try:
        claims = get_jwt()
        current_role = claims.get("role")
        current_user_id = int(get_jwt_identity())

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
            SELECT courseId, courseCode, courseName
            FROM Courses
            WHERE courseId = %s
            """,
            (course_id,)
        )
        course = cursor.fetchone()

        if not course:
            return error_response("Course not found", 404)

        if not is_course_member(cursor, current_user_id, current_role, course_id):
            return error_response("You are not allowed to create a forum for this course", 403)

        cursor.execute(
            """
            INSERT INTO Forums (courseId, title, createdByUserId)
            VALUES (%s, %s, %s)
            """,
            (course_id, title, current_user_id)
        )

        forum_id = cursor.lastrowid
        connection.commit()

        return success_response(
            "Forum created successfully",
            {
                "forum": {
                    "forumId": forum_id,
                    "courseId": course_id,
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