from app.mongo.dbConnection import mongo
import bcrypt
from flask_jwt_extended import create_access_token

class AuthService:
    @staticmethod
    def register_user(email: str, password: str) -> tuple[dict, int]:
        """Register a new user"""
        if mongo.identifier_users.find_one({"email": email}):
            return {"error": "User already exists"}, 400

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        mongo.identifier_users.insert_one({"email": email, "password": hashed_password})
        
        return {"message": "User registered"}, 201

    @staticmethod
    def login_user(email: str, password: str) -> tuple[dict, int]:
        """Login a user and return JWT token"""
        user = mongo.identifier_users.find_one({"email": email})

        if not user or not bcrypt.checkpw(password.encode(), user["password"]):
            return {"error": "Invalid credentials"}, 401

        token = create_access_token(identity=email)
        return {"access_token": token}, 200 