from flask import Blueprint, request, jsonify
from app.auth.services import AuthService

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    response, status_code = AuthService.register_user(email, password)
    return jsonify(response), status_code

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    response, status_code = AuthService.login_user(email, password)
    return jsonify(response), status_code 