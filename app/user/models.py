class MongoModels:
    def __init__(self, mongo_uri):
        client = MongoClient(mongo_uri)
        self.db = client.systemdb
        self.users = self.db.identifier_users
        self.products = self.db.identifier_products