from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.user.services import ShopifyService
from app.mongo.dbConnection import mongo

api = Blueprint("user", __name__)

# Shopify Product CRUD Operations
@api.route("/products", methods=["POST"])
@jwt_required()
def create_product():
    data = request.get_json()
    product = ShopifyService.create_product(data)

    if product:
        mongo.identifier_products.insert_one(product)
        return jsonify(product), 201
    return jsonify({"error": "Product creation failed"}), 400

@api.route("/products", methods=["GET"])
@jwt_required()
def get_products():
    products = ShopifyService.get_products()
    return jsonify(products), 200

@api.route("/products/<string:product_id>", methods=["GET"])
@jwt_required()
def get_product(product_id):
    product = ShopifyService.get_product(product_id)
    if product:
        return jsonify(product), 200
    return jsonify({"error": "Product not found"}), 404

@api.route("/products/<string:product_id>", methods=["PUT"])
@jwt_required()
def update_product(product_id):
    data = request.get_json()
    updated_product = ShopifyService.update_product(product_id, data)

    if updated_product:
        mongo.identifier_products.update_one({"id": product_id}, {"$set": updated_product})
        return jsonify(updated_product), 200
    return jsonify({"error": "Update failed"}), 400

@api.route("/products/<string:product_id>", methods=["DELETE"])
@jwt_required()
def delete_product(product_id):
    success = ShopifyService.delete_product(product_id)

    if success:
        mongo.identifier_products.delete_one({"id": product_id})
        return jsonify({"message": "Product deleted"}), 200
    return jsonify({"error": "Deletion failed"}), 400
