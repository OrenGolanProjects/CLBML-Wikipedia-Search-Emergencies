from flask import jsonify

def handle_exception(e):
    response = {
        "error": str(e)
    }
    return jsonify(response), 500
