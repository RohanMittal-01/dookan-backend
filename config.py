import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    # Database URIs
    MONGO_URI = os.getenv("MONGO_URI")
    POSTGRES_URI = os.getenv("POSTGRES_URI")

    #Shopify
    SHOPIFY_STORE = os.getenv("SHOPIFY_STORE")
    SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")