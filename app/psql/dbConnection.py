import psycopg2
from flask import current_app

postgres = None

def init_db(app):
    global postgres

    # PostgreSQL Connection
    postgres = psycopg2.connect(app.config["POSTGRES_URI"])
    with postgres.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS identifier_events (
                id SERIAL PRIMARY KEY,
                event_type VARCHAR(10),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id VARCHAR(255),
                product_id VARCHAR(255)
            );
        """)
    postgres.commit()
