from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.events.models import PostgresModels
from app.psql.dbConnection import postgres

api = Blueprint("events", __name__)

@api.route("/events", methods=["GET"])
@jwt_required()
def get_events():
    with postgres.cursor() as cursor:
        cursor.execute("SELECT * FROM identifier_events;")
        events = cursor.fetchall()
    return jsonify(events), 200
