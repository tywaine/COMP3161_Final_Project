from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt
from mysql.connector import Error

from app.db import get_db, close_db
from app.utils.response import error_response, success_response

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


def admin_only():
    claims = get_jwt()
    current_role = claims.get("role")
    return current_role == "admin"


@reports_bp.route("/courses-50-or-more-students", methods=["GET"])
@jwt_required()
def get_courses_with_50_or_more_students():
    connection = None
    cursor = None

    try:
        if not admin_only():
            return error_response("Only admins can view reports", 403)

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
                       SELECT courseId,
                              courseCode,
                              courseName,
                              description,
                              studentCount
                       FROM CoursesWith50OrMoreStudents
                       ORDER BY studentCount DESC, courseName
                       """)
        reports = cursor.fetchall()

        return success_response(
            "Courses with 50 or more students retrieved successfully",
            {"reports": reports}
        )

    except Error as e:
        return error_response("Database error", 500, e)

    except Exception as e:
        return error_response("Server error", 500, e)

    finally:
        close_db(connection, cursor)


@reports_bp.route("/students-5-or-more-courses", methods=["GET"])
@jwt_required()
def get_students_with_5_or_more_courses():
    connection = None
    cursor = None

    try:
        if not admin_only():
            return error_response("Only admins can view reports", 403)

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
                       SELECT studentId,
                              fullName,
                              email,
                              courseCount
                       FROM StudentsWith5OrMoreCourses
                       ORDER BY courseCount DESC, fullName
                       """)
        reports = cursor.fetchall()

        return success_response(
            "Students with 5 or more courses retrieved successfully",
            {"reports": reports}
        )

    except Error as e:
        return error_response("Database error", 500, e)

    except Exception as e:
        return error_response("Server error", 500, e)

    finally:
        close_db(connection, cursor)


@reports_bp.route("/lecturers-3-or-more-courses", methods=["GET"])
@jwt_required()
def get_lecturers_with_3_or_more_courses():
    connection = None
    cursor = None

    try:
        if not admin_only():
            return error_response("Only admins can view reports", 403)

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
                       SELECT lecturerId,
                              fullName,
                              email,
                              courseCount
                       FROM LecturersWith3OrMoreCourses
                       ORDER BY courseCount DESC, fullName
                       """)
        reports = cursor.fetchall()

        return success_response(
            "Lecturers with 3 or more courses retrieved successfully",
            {"reports": reports}
        )

    except Error as e:
        return error_response("Database error", 500, e)

    except Exception as e:
        return error_response("Server error", 500, e)

    finally:
        close_db(connection, cursor)


@reports_bp.route("/top-10-most-enrolled-courses", methods=["GET"])
@jwt_required()
def get_top_10_most_enrolled_courses():
    connection = None
    cursor = None

    try:
        if not admin_only():
            return error_response("Only admins can view reports", 403)

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                courseId,
                courseCode,
                courseName,
                description,
                studentCount
            FROM Top10MostEnrolledCourses
        """)
        reports = cursor.fetchall()

        return success_response(
            "Top 10 most enrolled courses retrieved successfully",
            {"reports": reports}
        )

    except Error as e:
        return error_response("Database error", 500, e)

    except Exception as e:
        return error_response("Server error", 500, e)

    finally:
        close_db(connection, cursor)


@reports_bp.route("/top-10-students-highest-overall-averages", methods=["GET"])
@jwt_required()
def get_top_10_students_highest_overall_averages():
    connection = None
    cursor = None

    try:
        if not admin_only():
            return error_response("Only admins can view reports", 403)

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                studentId,
                fullName,
                email,
                overallAverage
            FROM Top10StudentsHighestOverallAverages
        """)
        reports = cursor.fetchall()

        return success_response(
            "Top 10 students with highest overall averages retrieved successfully",
            {"reports": reports}
        )

    except Error as e:
        return error_response("Database error", 500, e)

    except Exception as e:
        return error_response("Server error", 500, e)

    finally:
        close_db(connection, cursor)