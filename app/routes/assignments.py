from datetime import datetime
from decimal import Decimal
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from mysql.connector import Error

from app.db import get_db, close_db
from app.utils.response import error_response, success_response

assignments_bp = Blueprint(
    "assignments",
    __name__,
    url_prefix="/api/assignments"
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


def is_enrolled_student(cursor, student_id, course_id):
    cursor.execute(
        """
        SELECT studentId
        FROM Enrollment
        WHERE studentId = %s AND courseId = %s
        """,
        (student_id, course_id)
    )
    return cursor.fetchone() is not None


def update_student_final_average(cursor, student_id, course_id):
    cursor.execute(
        """
        SELECT ROUND(AVG(s.grade), 2) AS finalAverage
        FROM Submissions s
        JOIN Assignments a ON s.assignmentId = a.assignmentId
        WHERE s.studentId = %s
          AND a.courseId = %s
          AND s.grade IS NOT NULL
        """,
        (student_id, course_id)
    )
    result = cursor.fetchone()
    final_average = result["finalAverage"] if result and result["finalAverage"] is not None else None

    cursor.execute(
        """
        UPDATE Enrollment
        SET finalGrade = %s
        WHERE studentId = %s AND courseId = %s
        """,
        (final_average, student_id, course_id)
    )

    return final_average


@assignments_bp.route("/course/<int:course_id>", methods=["POST"])
@jwt_required()
def create_assignment(course_id: int):
    connection = None
    cursor = None

    try:
        claims = get_jwt()
        current_role = claims.get("role")
        current_user_id = int(get_jwt_identity())

        if current_role != "lecturer":
            return error_response("Only lecturers can create assignments", 403)

        data = request.get_json()
        if not data:
            return error_response("Request body must be JSON")

        title = data.get("title")
        description = data.get("description")
        due_date = data.get("dueDate")
        total_marks = data.get("totalMarks", 100.00)

        if not title or not due_date:
            return error_response("title and dueDate are required")

        try:
            parsed_due_date = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return error_response("dueDate must be in YYYY-MM-DD HH:MM:SS format")

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
            return error_response("Only the assigned lecturer can create assignments for this course", 403)

        cursor.execute(
            """
            INSERT INTO Assignments (courseId, title, description, dueDate, totalMarks, createdByUserId)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                course_id,
                title,
                description,
                parsed_due_date,
                total_marks,
                current_user_id
            )
        )

        assignment_id = cursor.lastrowid
        connection.commit()

        return success_response(
            "Assignment created successfully",
            {
                "assignment": {
                    "assignmentId": assignment_id,
                    "courseId": course_id,
                    "title": title,
                    "description": description,
                    "dueDate": due_date,
                    "totalMarks": float(total_marks),
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


@assignments_bp.route("/course/<int:course_id>", methods=["GET"])
@jwt_required()
def get_assignments_for_course(course_id: int):
    connection = None
    cursor = None

    try:
        claims = get_jwt()
        current_role = claims.get("role")
        current_user_id = int(get_jwt_identity())

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT courseId, courseCode, courseName FROM Courses WHERE courseId = %s",
            (course_id,)
        )
        course = cursor.fetchone()

        if not course:
            return error_response("Course not found", 404)

        allowed = False

        if current_role == "admin":
            allowed = True
        elif current_role == "lecturer":
            allowed = is_assigned_lecturer(cursor, current_user_id, course_id)
        elif current_role == "student":
            allowed = is_enrolled_student(cursor, current_user_id, course_id)

        if not allowed:
            return error_response("You are not allowed to view assignments for this course", 403)

        cursor.execute(
            """
            SELECT a.assignmentId,
                   a.courseId,
                   a.title,
                   a.description,
                   a.dueDate,
                   a.totalMarks,
                   a.createdByUserId,
                   u.fullName AS createdByName
            FROM Assignments a
                     JOIN Users u ON a.createdByUserId = u.userId
            WHERE a.courseId = %s
            ORDER BY a.dueDate, a.assignmentId
            """,
            (course_id,)
        )
        assignments = [format_db_row(row) for row in cursor.fetchall()]

        return success_response(
            "Assignments retrieved successfully",
            {
                "course": format_db_row(course),
                "assignments": assignments
            }
        )

    except Error as e:
        return error_response("Database error", 500, e)

    except Exception as e:
        return error_response("Server error", 500, e)

    finally:
        close_db(connection, cursor)


@assignments_bp.route("/<int:assignment_id>/submit", methods=["POST"])
@jwt_required()
def submit_assignment(assignment_id):
    connection = None
    cursor = None

    try:
        claims = get_jwt()
        current_role = claims.get("role")
        current_user_id = int(get_jwt_identity())

        if current_role != "student":
            return error_response("Only students can submit assignments", 403)

        data = request.get_json()
        if not data:
            return error_response("Request body must be JSON")

        file_path = data.get("filePath")
        text_content = data.get("textContent")

        if not file_path and not text_content:
            return error_response("At least one of filePath or textContent is required")

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                a.assignmentId,
                a.courseId,
                a.title,
                a.dueDate
            FROM Assignments a
            WHERE a.assignmentId = %s
            """,
            (assignment_id,)
        )
        assignment = cursor.fetchone()

        if not assignment:
            return error_response("Assignment not found", 404)

        if not is_enrolled_student(cursor, current_user_id, assignment["courseId"]):
            return error_response("Only enrolled students can submit assignments for this course", 403)

        cursor.execute(
            """
            SELECT submissionId
            FROM Submissions
            WHERE assignmentId = %s AND studentId = %s
            """,
            (assignment_id, current_user_id)
        )
        existing_submission = cursor.fetchone()

        if existing_submission:
            return error_response("Student has already submitted this assignment", 409)

        cursor.execute(
            """
            INSERT INTO Submissions (assignmentId, studentId, filePath, textContent)
            VALUES (%s, %s, %s, %s)
            """,
            (assignment_id, current_user_id, file_path, text_content)
        )

        submission_id = cursor.lastrowid
        connection.commit()

        return success_response(
            "Assignment submitted successfully",
            {
                "submission": {
                    "submissionId": submission_id,
                    "assignmentId": assignment_id,
                    "studentId": current_user_id,
                    "filePath": file_path,
                    "textContent": text_content
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


@assignments_bp.route("/<int:assignment_id>/submissions", methods=["GET"])
@jwt_required()
def get_submissions_for_assignment(assignment_id):
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
                a.assignmentId,
                a.courseId,
                a.title
            FROM Assignments a
            WHERE a.assignmentId = %s
            """,
            (assignment_id,)
        )
        assignment = cursor.fetchone()

        if not assignment:
            return error_response("Assignment not found", 404)

        allowed = False
        if current_role == "lecturer":
            allowed = is_assigned_lecturer(cursor, current_user_id, assignment["courseId"])
        elif current_role == "admin":
            allowed = True

        if not allowed:
            return error_response("Only the assigned lecturer or an admin can view submissions", 403)

        cursor.execute(
            """
            SELECT s.submissionId,
                   s.assignmentId,
                   s.studentId,
                   u.fullName AS studentName,
                   s.submittedAt,
                   s.filePath,
                   s.textContent,
                   s.grade,
                   s.feedback
            FROM Submissions s
                     JOIN Users u ON s.studentId = u.userId
            WHERE s.assignmentId = %s
            ORDER BY s.submittedAt, s.submissionId
            """,
            (assignment_id,)
        )
        submissions = [format_db_row(row) for row in cursor.fetchall()]

        return success_response(
            "Submissions retrieved successfully",
            {
                "assignment": format_db_row(assignment),
                "submissions": submissions
            }
        )

    except Error as e:
        return error_response("Database error", 500, e)

    except Exception as e:
        return error_response("Server error", 500, e)

    finally:
        close_db(connection, cursor)


@assignments_bp.route("/submissions/<int:submission_id>/grade", methods=["PUT"])
@jwt_required()
def grade_submission(submission_id):
    connection = None
    cursor = None

    try:
        claims = get_jwt()
        current_role = claims.get("role")
        current_user_id = int(get_jwt_identity())

        if current_role != "lecturer":
            return error_response("Only lecturers can grade submissions", 403)

        data = request.get_json()
        if not data:
            return error_response("Request body must be JSON")

        grade = data.get("grade")
        feedback = data.get("feedback")

        if grade is None:
            return error_response("grade is required")

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                s.submissionId,
                s.studentId,
                s.assignmentId,
                a.courseId,
                a.totalMarks
            FROM Submissions s
            JOIN Assignments a ON s.assignmentId = a.assignmentId
            WHERE s.submissionId = %s
            """,
            (submission_id,)
        )
        submission = cursor.fetchone()

        if not submission:
            return error_response("Submission not found", 404)

        if not is_assigned_lecturer(cursor, current_user_id, submission["courseId"]):
            return error_response("Only the assigned lecturer can grade submissions for this course", 403)

        try:
            grade = float(grade)
        except (TypeError, ValueError):
            return error_response("grade must be a number")

        if grade < 0 or grade > float(submission["totalMarks"]):
            return error_response(f"grade must be between 0 and {submission['totalMarks']}")

        cursor.execute(
            """
            UPDATE Submissions
            SET grade = %s, feedback = %s
            WHERE submissionId = %s
            """,
            (grade, feedback, submission_id)
        )

        final_average = update_student_final_average(
            cursor,
            submission["studentId"],
            submission["courseId"]
        )

        connection.commit()

        return success_response(
            "Submission graded successfully",
            {
                "gradedSubmission": {
                    "submissionId": submission_id,
                    "assignmentId": submission["assignmentId"],
                    "studentId": submission["studentId"],
                    "grade": float(grade),
                    "feedback": feedback
                },
                "updatedCourseFinalAverage": float(final_average) if final_average is not None else None
            }
        )

    except Error as e:
        return error_response("Database error", 500, e)

    except Exception as e:
        return error_response("Server error", 500, e)

    finally:
        close_db(connection, cursor)


@assignments_bp.route("/upcoming", methods=["GET"])
@jwt_required()
def get_upcoming_assignments():
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
                SELECT a.assignmentId, a.title, a.dueDate, c.courseCode
                FROM Assignments a
                JOIN Courses c ON a.courseId = c.courseId
                WHERE a.dueDate >= NOW()
                ORDER BY a.dueDate ASC
                LIMIT 5
            """
            cursor.execute(query)
        elif current_role == "student":
            query = """
                SELECT a.assignmentId, a.title, a.dueDate, c.courseCode
                FROM Enrollment e
                JOIN Assignments a ON e.courseId = a.courseId
                JOIN Courses c ON a.courseId = c.courseId
                WHERE e.studentId = %s AND a.dueDate >= NOW()
                ORDER BY a.dueDate ASC
                LIMIT 5
            """
            cursor.execute(query, (current_user_id,))
        else: # Lecturer
            query = """
                SELECT a.assignmentId, a.title, a.dueDate, c.courseCode
                FROM Teaching t
                JOIN Assignments a ON t.courseId = a.courseId
                JOIN Courses c ON a.courseId = c.courseId
                WHERE t.lecturerId = %s AND a.dueDate >= NOW()
                ORDER BY a.dueDate ASC
                LIMIT 5
            """
            cursor.execute(query, (current_user_id,))

        assignments = [format_db_row(row) for row in cursor.fetchall()]
        return success_response("Upcoming assignments retrieved", {"assignments": assignments})
    except Error as e:
        return error_response("Database error", 500, e)
    except Exception as e:
        return error_response("Server error", 500, e)
    finally:
        close_db(connection, cursor)


@assignments_bp.route("/course/<int:course_id>/my-submissions", methods=["GET"])
@jwt_required()
def get_my_submissions(course_id: int):
    connection = None
    cursor = None
    try:
        claims = get_jwt()
        current_role = claims.get("role")
        current_user_id = int(get_jwt_identity())

        if current_role != "student":
            return error_response("Only students can view their own submissions", 403)

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT s.submissionId, s.assignmentId, s.submittedAt, s.grade, s.feedback
            FROM Submissions s
            JOIN Assignments a ON s.assignmentId = a.assignmentId
            WHERE s.studentId = %s AND a.courseId = %s
            """,
            (current_user_id, course_id)
        )
        submissions = [format_db_row(row) for row in cursor.fetchall()]

        return success_response("Submissions retrieved", {"submissions": submissions})

    except Error as e:
        return error_response("Database error", 500, e)
    except Exception as e:
        return error_response("Server error", 500, e)
    finally:
        close_db(connection, cursor)