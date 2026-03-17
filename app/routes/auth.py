from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from mysql.connector import Error

from app.db import get_db

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register_user():
    connection = None
    cursor = None

    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        user_id = data.get("userId")
        full_name = data.get("fullName")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role")
        department = data.get("department")  # only for lecturers

        # Basic required fields
        if not user_id or not full_name or not email or not password or not role:
            return jsonify({
                "error": "userId, fullName, email, password, and role are required"
            }), 400

        # Validate role
        if role not in ["student", "lecturer", "admin"]:
            return jsonify({
                "error": "role must be one of: student, lecturer, admin"
            }), 400

        # Validate userId is a 9-digit number
        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            return jsonify({"error": "userId must be a number"}), 400

        if user_id < 100000000 or user_id > 999999999:
            return jsonify({"error": "userId must be a 9-digit number"}), 400

        # Lecturer must provide department
        if role == "lecturer" and not department:
            return jsonify({"error": "department is required for lecturer registration"}), 400

        password_hash = generate_password_hash(password)

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        # Check if userId already exists
        cursor.execute("SELECT userId FROM Users WHERE userId = %s", (user_id,))
        existing_user_id = cursor.fetchone()
        if existing_user_id:
            return jsonify({"error": "userId already exists"}), 409

        # Check if email already exists
        cursor.execute("SELECT userId FROM Users WHERE email = %s", (email,))
        existing_email = cursor.fetchone()
        if existing_email:
            return jsonify({"error": "email already exists"}), 409

        connection.start_transaction()

        # Insert into Users
        insert_user_sql = """
            INSERT INTO Users (userId, fullName, passwordHash, email, role)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_user_sql, (user_id, full_name, password_hash, email, role))

        # Insert into subtype table
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

        return jsonify({
            "message": "User registered successfully",
            "user": {
                "userId": user_id,
                "fullName": full_name,
                "email": email,
                "role": role
            }
        }), 201

    except Error as e:
        if connection:
            connection.rollback()
        return jsonify({
            "error": "Database error",
            "details": str(e)
        }), 500

    except Exception as e:
        if connection:
            connection.rollback()
        return jsonify({
            "error": "Server error",
            "details": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@auth_bp.route("/login", methods=["POST"])
def login_user():
    connection = None
    cursor = None

    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        user_id = data.get("userId")
        password = data.get("password")

        if not user_id or not password:
            return jsonify({"error": "userId and password are required"}), 400

        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            return jsonify({"error": "userId must be a number"}), 400

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
            return jsonify({"error": "Invalid credentials"}), 401

        if not check_password_hash(user["passwordHash"], password):
            return jsonify({"error": "Invalid credentials"}), 401

        access_token = create_access_token(
            identity=str(user["userId"]),
            additional_claims={"role": user["role"]}
        )

        return jsonify({
            "message": "Login successful",
            "accessToken": access_token,
            "user": {
                "userId": user["userId"],
                "fullName": user["fullName"],
                "email": user["email"],
                "role": user["role"]
            }
        }), 200

    except Error as e:
        return jsonify({
            "error": "Database error",
            "details": str(e)
        }), 500

    except Exception as e:
        return jsonify({
            "error": "Server error",
            "details": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()