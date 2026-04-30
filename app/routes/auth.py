from flask import Blueprint, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from mysql.connector import Error

from app.db import get_db, close_db
from app.utils.response import error_response, success_response
from datetime import timedelta

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register_user():
    connection = None
    cursor = None

    try:
        data = request.get_json()

        if not data:
            return error_response("Request body must be JSON")

        user_id = data.get("userId")
        full_name = data.get("fullName")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role")
        department = data.get("department")

        if not user_id or not full_name or not email or not password or not role:
            return error_response("userId, fullName, email, password, and role are required")

        if role not in ["student", "lecturer", "admin"]:
            return error_response("role must be one of: student, lecturer, admin")

        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            return error_response("userId must be a number")

        if user_id < 100000000 or user_id > 999999999:
            return error_response("userId must be a 9-digit number")

        if role == "lecturer" and not department:
            return error_response("department is required for lecturer registration")

        password_hash = generate_password_hash(password)

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT userId FROM Users WHERE userId = %s", (user_id,))
        existing_user_id = cursor.fetchone()
        if existing_user_id:
            return error_response("userId already exists", 409)

        cursor.execute("SELECT userId FROM Users WHERE email = %s", (email,))
        existing_email = cursor.fetchone()
        if existing_email:
            return error_response("email already exists", 409)

        insert_user_sql = """
                          INSERT INTO Users (userId, fullName, passwordHash, email, role)
                          VALUES (%s, %s, %s, %s, %s)
                          """
        cursor.execute(insert_user_sql, (user_id, full_name, password_hash, email, role))

        if role == "student":
            insert_student_sql = """
                                 INSERT INTO Students (userId, gpa)
                                 VALUES (%s, %s)
                                 """
            cursor.execute(insert_student_sql, (user_id, 0.00))

        elif role == "lecturer":
            insert_lecturer_sql = """
                                  INSERT INTO Lecturers (userId, department)
                                  VALUES (%s, %s)
                                  """
            cursor.execute(insert_lecturer_sql, (user_id, department))

        elif role == "admin":
            insert_admin_sql = """
                               INSERT INTO Admins (userId)
                               VALUES (%s)
                               """
            cursor.execute(insert_admin_sql, (user_id,))

        connection.commit()

        return success_response(
            "User registered successfully",
            {
                "userId": user_id,
                "fullName": full_name,
                "email": email,
                "role": role
            },
            201
        )

    except Error as e:
        return error_response("Database error", 500, e)

    except Exception as e:
        return error_response("Server error", 500, e)

    finally:
        close_db(connection, cursor)


@auth_bp.route("/login", methods=["POST"])
def login_user():
    connection = None
    cursor = None

    try:
        data = request.get_json()

        if not data:
            return error_response("Request body must be JSON")

        user_id = data.get("userId")
        password = data.get("password")

        if not user_id or not password:
            return error_response("userId and password are required")

        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            return error_response("userId must be a number")

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        login_sql = """
            SELECT userId, fullName, passwordHash, email, role
            FROM Users
            WHERE userId = %s
        """
        cursor.execute(login_sql, (user_id,))
        user = cursor.fetchone()

        if not user:
            return error_response("Invalid credentials", 401)

        if not check_password_hash(user["passwordHash"], password):
            return error_response("Invalid credentials", 401)

        access_token = create_access_token(
            identity=str(user["userId"]),
            additional_claims={"role": user["role"]},
            expires_delta=timedelta(days=1)
        )

        return success_response(
            "Login successful",
            {
                "accessToken": access_token,
                "user": {
                    "userId": user["userId"],
                    "fullName": user["fullName"],
                    "email": user["email"],
                    "role": user["role"]
                }
            }
        )

    except Error as e:
        return error_response("Database error", 500, e)

    except Exception as e:
        return error_response("Server error", 500, e)

    finally:
        close_db(connection, cursor)