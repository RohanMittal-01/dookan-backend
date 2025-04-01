from pymongo import MongoClient

mongo = None

def init_db(app):
    global mongo

    # MongoDB Connection
    mongo = MongoClient(app.config["MONGO_URI"]).systemdb