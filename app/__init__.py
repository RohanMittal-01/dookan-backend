from flask import Flask
from flask_jwt_extended import JWTManager
from app.mongo.dbConnection import init_db as mongo_init_db
from app.psql.dbConnection import init_db as psql_init_db

def create_app():
    app = Flask(__name__)

    # Load configurations
    app.config.from_object('config.Config')

    # Initialize DB
    mongo_init_db(app)
    psql_init_db(app)

    # Register blueprints
    from app.user.routes import api as user_bp
    from app.events.routes import api as events_bp
    from app.auth.routes import auth as auth_bp
    
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api")
    app.register_blueprint(events_bp, url_prefix="/api")

    # Setup JWT
    jwt = JWTManager(app)

    return app