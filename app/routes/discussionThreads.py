from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from mysql.connector import Error

from app.db import get_db, close_db
from app.utils.response import error_response, success_response

threads_bp = Blueprint("threads", __name__, url_prefix="/api/threads")

@threads_bp.route("/forum/<int:forum_id>", methods=["GET"])
@jwt_required()
def get_forum_threads(forum_id):
    connection = None
    cursor = None
    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT threadId, forumId, createdByUserId, title, createdAt
            FROM DiscussionThreads
            WHERE forumId = %s
            ORDER BY createdAt DESC
        """, (forum_id,))
        threads = cursor.fetchall()

        return success_response("Threads retrieved successfully", {"threads": threads})
    except Error as e:
        return error_response("Database error", 500, e)
    finally:
        close_db(connection, cursor)


@threads_bp.route("/<int:thread_id>/posts", methods=["GET"])
@jwt_required()
def get_thread_posts(thread_id):
    connection = None
    cursor = None
    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        # Retrieve posts for a thread, including full name of user who posted
        query = """
            SELECT p.postId, p.threadId, p.userId, p.parentPostId, p.content, p.createdAt, u.fullName AS authorName
            FROM Posts p
            JOIN Users u ON p.userId = u.userId
            WHERE p.threadId = %s
            ORDER BY p.createdAt ASC
        """
        cursor.execute(query, (thread_id,))
        posts = cursor.fetchall()

        return success_response("Posts retrieved successfully", {"posts": posts})
    except Error as e:
        return error_response("Database error", 500, e)
    finally:
        close_db(connection, cursor)


@threads_bp.route("/forum/<int:forum_id>", methods=["POST"])
@jwt_required()
def create_thread(forum_id):
    connection = None
    cursor = None
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return error_response("Request body must be JSON")

        title = data.get("title")
        content = data.get("content")

        if not title or not content:
            return error_response("title and content are required", 400)

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        # Check if forum exists
        cursor.execute("SELECT forumId FROM Forums WHERE forumId = %s", (forum_id,))
        if not cursor.fetchone():
            return error_response("Forum not found", 404)

        # 1. Insert DiscussionThread
        insert_thread_sql = """
            INSERT INTO DiscussionThreads (forumId, createdByUserId, title)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_thread_sql, (forum_id, user_id, title))
        thread_id = cursor.lastrowid

        # 2. Insert initial Post
        insert_post_sql = """
            INSERT INTO Posts (threadId, userId, parentPostId, content)
            VALUES (%s, %s, NULL, %s)
        """
        cursor.execute(insert_post_sql, (thread_id, user_id, content))
        post_id = cursor.lastrowid

        connection.commit()

        return success_response(
            "Thread created successfully",
            {
                "thread": {
                    "threadId": thread_id,
                    "forumId": forum_id,
                    "createdByUserId": int(user_id),
                    "title": title
                },
                "initialPost": {
                    "postId": post_id,
                    "content": content
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


@threads_bp.route("/<int:thread_id>/reply", methods=["POST"])
@jwt_required()
def reply_to_thread(thread_id):
    connection = None
    cursor = None
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return error_response("Request body must be JSON")

        content = data.get("content")
        parent_post_id = data.get("parentPostId")

        if not content:
            return error_response("content is required", 400)

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        # Check if thread exists
        cursor.execute("SELECT threadId FROM DiscussionThreads WHERE threadId = %s", (thread_id,))
        if not cursor.fetchone():
            return error_response("Thread not found", 404)

        # If replying to a specific post, verify the post exists and belongs to the same thread
        if parent_post_id is not None:
            cursor.execute("SELECT postId FROM Posts WHERE postId = %s AND threadId = %s", (parent_post_id, thread_id))
            if not cursor.fetchone():
                return error_response("Parent post not found or does not belong to this thread", 404)

        insert_sql = """
            INSERT INTO Posts (threadId, userId, parentPostId, content)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_sql, (thread_id, user_id, parent_post_id, content))
        connection.commit()

        post_id = cursor.lastrowid

        return success_response(
            "Reply created successfully",
            {
                "post": {
                    "postId": post_id,
                    "threadId": thread_id,
                    "userId": int(user_id),
                    "parentPostId": parent_post_id,
                    "content": content
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