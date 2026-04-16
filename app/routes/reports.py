from flask import Blueprint, request
from mysql.connector import Error

from app.db import get_db, close_db
from app.utils.response import error_response, success_response

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


@reports_bp.route("/top-students", methods=["GET"])
def top_students():
    connection = None
    cursor = None

    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM top_students")
        results = cursor.fetchall()

        return success_response("Top students", results)

    except Error as e:
        return error_response("Database error", 500, e)

    finally:
        close_db(connection, cursor)