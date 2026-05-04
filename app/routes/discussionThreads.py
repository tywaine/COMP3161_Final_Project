from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from mysql.connector import Error

from app.db import get_db, close_db
from app.utils.response import error_response, success_response

discussion_threads_bp = Blueprint(
    "discussion_threads",
    __name__,
    url_prefix="/api/discussion-threads"
)


def get_forum_course_and_membership(cursor, forum_id, user_id, role):
    cursor.execute(
        """
        SELECT
            f.forumId,
            f.courseCode,
            f.title AS forumTitle,
            c.courseCode,
            c.courseName
        FROM Forums f
        JOIN Courses c ON f.courseCode = c.courseCode
        WHERE f.forumId = %s
        """,
        (forum_id,)
    )
    forum = cursor.fetchone()

    if not forum:
        return None, False

    if role == "admin":
        return forum, True

    if role == "lecturer":
        cursor.execute(
            """
            SELECT lecturerId
            FROM Teaching
            WHERE lecturerId = %s AND courseCode = %s
            """,
            (user_id, forum["courseCode"])
        )
        return forum, cursor.fetchone() is not None

    if role == "student":
        cursor.execute(
            """
            SELECT studentId
            FROM Enrollment
            WHERE studentId = %s AND courseCode = %s
            """,
            (user_id, forum["courseCode"])
        )
        return forum, cursor.fetchone() is not None

    return forum, False


@discussion_threads_bp.route("/forum/<int:forum_id>", methods=["GET"])
@jwt_required()
def get_threads_for_forum(forum_id):
    connection = None
    cursor = None

    try:
        claims = get_jwt()
        current_role = claims.get("role")
        current_user_id = int(get_jwt_identity())

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        forum, allowed = get_forum_course_and_membership(
            cursor,
            forum_id,
            current_user_id,
            current_role
        )

        if not forum:
            return error_response("Forum not found", 404)

        if not allowed:
            return error_response("You are not allowed to view threads for this forum", 403)

        cursor.execute(
            """
            SELECT
                dt.threadId,
                dt.forumId,
                dt.createdByUserId,
                u.fullName AS createdByName,
                dt.title,
                dt.createdAt,
                (
                    SELECT COUNT(*)
                    FROM Posts p
                    WHERE p.threadId = dt.threadId
                ) AS postCount
            FROM DiscussionThreads dt
            JOIN Users u ON dt.createdByUserId = u.userId
            WHERE dt.forumId = %s
            ORDER BY dt.createdAt DESC
            """,
            (forum_id,)
        )
        threads = cursor.fetchall()

        return success_response(
            "Discussion threads retrieved successfully",
            {
                "forum": forum,
                "threads": threads
            }
        )

    except Error as e:
        return error_response("Database error", 500, e)

    except Exception as e:
        return error_response("Server error", 500, e)

    finally:
        close_db(connection, cursor)


@discussion_threads_bp.route("/forum/<int:forum_id>", methods=["POST"])
@jwt_required()
def create_thread(forum_id):
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
        content = data.get("content")

        if not title or not content:
            return error_response("title and content are required")

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        forum, allowed = get_forum_course_and_membership(
            cursor,
            forum_id,
            current_user_id,
            current_role
        )

        if not forum:
            return error_response("Forum not found", 404)

        if not allowed:
            return error_response("You are not allowed to create a thread in this forum", 403)

        cursor.execute(
            """
            INSERT INTO DiscussionThreads (forumId, createdByUserId, title)
            VALUES (%s, %s, %s)
            """,
            (forum_id, current_user_id, title)
        )
        thread_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO Posts (threadId, userId, parentPostId, content)
            VALUES (%s, %s, %s, %s)
            """,
            (thread_id, current_user_id, None, content)
        )
        first_post_id = cursor.lastrowid

        connection.commit()

        return success_response(
            "Discussion thread created successfully",
            {
                "thread": {
                    "threadId": thread_id,
                    "forumId": forum_id,
                    "createdByUserId": current_user_id,
                    "title": title,
                    "firstPostId": first_post_id,
                    "firstPostContent": content
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


@discussion_threads_bp.route("/<int:thread_id>/posts", methods=["GET"])
@jwt_required()
def get_posts_for_thread(thread_id):
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
            SELECT
                dt.threadId,
                dt.title AS threadTitle,
                dt.forumId,
                f.courseCode
            FROM DiscussionThreads dt
            JOIN Forums f ON dt.forumId = f.forumId
            WHERE dt.threadId = %s
            """,
            (thread_id,)
        )
        thread = cursor.fetchone()

        if not thread:
            return error_response("Thread not found", 404)

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
                (current_user_id, thread["courseCode"])
            )
            allowed = cursor.fetchone() is not None
        elif current_role == "student":
            cursor.execute(
                """
                SELECT studentId
                FROM Enrollment
                WHERE studentId = %s AND courseCode = %s
                """,
                (current_user_id, thread["courseCode"])
            )
            allowed = cursor.fetchone() is not None

        if not allowed:
            return error_response("You are not allowed to view posts for this thread", 403)

        cursor.execute(
            """
            SELECT p.postId,
                   p.threadId,
                   p.userId,
                   u.fullName,
                   p.parentPostId,
                   p.content,
                   p.createdAt
            FROM Posts p
                     JOIN Users u ON p.userId = u.userId
            WHERE p.threadId = %s
            ORDER BY p.createdAt, p.postId
            """,
            (thread_id,)
        )
        posts = cursor.fetchall()

        return success_response(
            "Thread posts retrieved successfully",
            {
                "thread": thread,
                "posts": posts
            }
        )

    except Error as e:
        return error_response("Database error", 500, e)

    except Exception as e:
        return error_response("Server error", 500, e)

    finally:
        close_db(connection, cursor)


@discussion_threads_bp.route("/<int:thread_id>/reply", methods=["POST"])
@jwt_required()
def reply_to_thread(thread_id):
    connection = None
    cursor = None

    try:
        claims = get_jwt()
        current_role = claims.get("role")
        current_user_id = int(get_jwt_identity())

        data = request.get_json()
        if not data:
            return error_response("Request body must be JSON")

        content = data.get("content")
        parent_post_id = data.get("parentPostId")

        if not content:
            return error_response("content is required")

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                dt.threadId,
                dt.title AS threadTitle,
                dt.forumId,
                f.courseCode
            FROM DiscussionThreads dt
            JOIN Forums f ON dt.forumId = f.forumId
            WHERE dt.threadId = %s
            """,
            (thread_id,)
        )
        thread = cursor.fetchone()

        if not thread:
            return error_response("Thread not found", 404)

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
                (current_user_id, thread["courseCode"])
            )
            allowed = cursor.fetchone() is not None
        elif current_role == "student":
            cursor.execute(
                """
                SELECT studentId
                FROM Enrollment
                WHERE studentId = %s AND courseCode = %s
                """,
                (current_user_id, thread["courseCode"])
            )
            allowed = cursor.fetchone() is not None

        if not allowed:
            return error_response("You are not allowed to reply in this thread", 403)

        if parent_post_id is not None:
            cursor.execute(
                """
                SELECT postId
                FROM Posts
                WHERE postId = %s AND threadId = %s
                """,
                (parent_post_id, thread_id)
            )
            parent_post = cursor.fetchone()

            if not parent_post:
                return error_response("parentPostId does not exist in this thread", 404)

        cursor.execute(
            """
            INSERT INTO Posts (threadId, userId, parentPostId, content)
            VALUES (%s, %s, %s, %s)
            """,
            (thread_id, current_user_id, parent_post_id, content)
        )

        post_id = cursor.lastrowid
        connection.commit()

        return success_response(
            "Reply added successfully",
            {
                "post": {
                    "postId": post_id,
                    "threadId": thread_id,
                    "userId": current_user_id,
                    "parentPostId": parent_post_id,
                    "content": content
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