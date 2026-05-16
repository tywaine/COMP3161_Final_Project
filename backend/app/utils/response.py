from flask import jsonify


def error_response(message, status_code=400, details=None):
    response = {
        "error": message
    }

    if details:
        response["details"] = str(details)

    return jsonify(response), status_code


def success_response(message, data=None, status_code=200):
    response = {
        "message": message
    }

    if data:
        response.update(data)

    return jsonify(response), status_code