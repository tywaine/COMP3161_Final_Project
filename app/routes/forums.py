from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from mysql.connector import Error

from app.db import get_db, close_db
from app.utils.response import error_response, success_response

forums_bp = Blueprint("forums", __name__, url_prefix="/api/forums")

@forums_bp.route("/course/<int:course_id>", methods=["GET"])
@jwt_required()
def get_course_forums(course_id):
    connection = None
    cursor = None
    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT forumId, courseId, title, createdByUserId, createdAt
            FROM Forums
            WHERE courseId = %s
            ORDER BY createdAt DESC
        """, (course_id,))
        forums = cursor.fetchall()

        return success_response("Forums retrieved successfully", {"forums": forums})
    except Error as e:
        return error_response("Database error", 500, e)
    finally:
        close_db(connection, cursor)

@forums_bp.route("/course/<int:course_id>", methods=["POST"])
@jwt_required()
def create_forum(course_id):
    connection = None
    cursor = None
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return error_response("Request body must be JSON")

        title = data.get("title")

        if not title:
            return error_response("title is required", 400)

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        # Check if course exists
        cursor.execute("SELECT courseId FROM Courses WHERE courseId = %s", (course_id,))
        if not cursor.fetchone():
            return error_response("Course not found", 404)

        insert_sql = """
            INSERT INTO Forums (courseId, title, createdByUserId)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_sql, (course_id, title, user_id))
        connection.commit()

        forum_id = cursor.lastrowid

        return success_response(
            "Forum created successfully",
            {
                "forum": {
                    "forumId": forum_id,
                    "courseId": course_id,
                    "title": title,
                    "createdByUserId": int(user_id)
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