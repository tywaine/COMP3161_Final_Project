from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from mysql.connector import Error

from app.db import get_db, close_db
from app.utils.response import error_response, success_response

course_content_bp = Blueprint(
    "course_content",
    __name__,
    url_prefix="/api/course-content"
)


def is_assigned_lecturer(cursor, lecturer_id, course_id):
    cursor.execute(
        """
        SELECT lecturerId
        FROM Teaching
        WHERE lecturerId = %s AND courseId = %s
        """,
        (lecturer_id, course_id)
    )
    return cursor.fetchone() is not None


def is_course_member(cursor, user_id, role, course_id):
    if role == "admin":
        return True

    if role == "lecturer":
        return is_assigned_lecturer(cursor, user_id, course_id)

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


@course_content_bp.route("/course/<int:course_id>/sections", methods=["POST"])
@jwt_required()
def create_section(course_id):
    connection = None
    cursor = None

    try:
        claims = get_jwt()
        current_role = claims.get("role")
        current_user_id = int(get_jwt_identity())

        if current_role != "lecturer":
            return error_response("Only lecturers can create sections", 403)

        data = request.get_json()
        if not data:
            return error_response("Request body must be JSON")

        title = data.get("title")
        position = data.get("position")

        if not title or position is None:
            return error_response("title and position are required")

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT courseId, courseCode, courseName FROM Courses WHERE courseId = %s",
            (course_id,)
        )
        course = cursor.fetchone()

        if not course:
            return error_response("Course not found", 404)

        if not is_assigned_lecturer(cursor, current_user_id, course_id):
            return error_response("Only the assigned lecturer can create sections for this course", 403)

        cursor.execute(
            """
            INSERT INTO Sections (courseId, title, position)
            VALUES (%s, %s, %s)
            """,
            (course_id, title, position)
        )

        section_id = cursor.lastrowid
        connection.commit()

        return success_response(
            "Section created successfully",
            {
                "section": {
                    "sectionId": section_id,
                    "courseId": course_id,
                    "title": title,
                    "position": position
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


@course_content_bp.route("/sections/<int:section_id>/items", methods=["POST"])
@jwt_required()
def add_section_item(section_id):
    connection = None
    cursor = None

    try:
        claims = get_jwt()
        current_role = claims.get("role")
        current_user_id = int(get_jwt_identity())

        if current_role != "lecturer":
            return error_response("Only lecturers can add course content", 403)

        data = request.get_json()
        if not data:
            return error_response("Request body must be JSON")

        title = data.get("title")
        content_type = data.get("contentType")
        content_url = data.get("contentUrl")
        file_path = data.get("filePath")
        description = data.get("description")

        if not title or not content_type:
            return error_response("title and contentType are required")

        allowed_types = {"link", "file", "slide", "note"}
        if content_type not in allowed_types:
            return error_response("contentType must be one of: link, file, slide, note")

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                s.sectionId,
                s.courseId,
                s.title AS sectionTitle,
                c.courseCode,
                c.courseName
            FROM Sections s
            JOIN Courses c ON s.courseId = c.courseId
            WHERE s.sectionId = %s
            """,
            (section_id,)
        )
        section = cursor.fetchone()

        if not section:
            return error_response("Section not found", 404)

        if not is_assigned_lecturer(cursor, current_user_id, section["courseId"]):
            return error_response("Only the assigned lecturer can add content to this course", 403)

        cursor.execute(
            """
            INSERT INTO SectionItems
            (sectionId, title, contentType, contentUrl, filePath, description, uploadedByUserId)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                section_id,
                title,
                content_type,
                content_url,
                file_path,
                description,
                current_user_id
            )
        )

        section_item_id = cursor.lastrowid
        connection.commit()

        return success_response(
            "Course content added successfully",
            {
                "sectionItem": {
                    "sectionItemId": section_item_id,
                    "sectionId": section_id,
                    "title": title,
                    "contentType": content_type,
                    "contentUrl": content_url,
                    "filePath": file_path,
                    "description": description,
                    "uploadedByUserId": current_user_id
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


@course_content_bp.route("/course/<int:course_id>", methods=["GET"])
@jwt_required()
def get_course_content(course_id):
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
            SELECT courseId, courseCode, courseName, description
            FROM Courses
            WHERE courseId = %s
            """,
            (course_id,)
        )
        course = cursor.fetchone()

        if not course:
            return error_response("Course not found", 404)

        if not is_course_member(cursor, current_user_id, current_role, course_id):
            return error_response("You are not allowed to view content for this course", 403)

        cursor.execute(
            """
            SELECT s.sectionId,
                   s.courseId,
                   s.title,
                   s.position
            FROM Sections s
            WHERE s.courseId = %s
            ORDER BY s.position, s.sectionId
            """,
            (course_id,)
        )
        sections = cursor.fetchall()

        for section in sections:
            cursor.execute(
                """
                SELECT si.sectionItemId,
                       si.sectionId,
                       si.title,
                       si.contentType,
                       si.contentUrl,
                       si.filePath,
                       si.description,
                       si.uploadedByUserId,
                       u.fullName AS uploadedByName,
                       si.createdAt
                FROM SectionItems si
                         JOIN Users u ON si.uploadedByUserId = u.userId
                WHERE si.sectionId = %s
                ORDER BY si.createdAt, si.sectionItemId
                """,
                (section["sectionId"],)
            )
            section["items"] = cursor.fetchall()

        return success_response(
            "Course content retrieved successfully",
            {
                "course": course,
                "sections": sections
            }
        )

    except Error as e:
        return error_response("Database error", 500, e)

    except Exception as e:
        return error_response("Server error", 500, e)

    finally:
        close_db(connection, cursor)