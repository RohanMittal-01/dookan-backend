import psycopg2

class PostgresModels:
    def __init__(self, postgres_uri):
        self.conn = psycopg2.connect(postgres_uri)
        self.create_events_table()

    def create_events_table(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS systemdb.identifier_events (
                    id SERIAL PRIMARY KEY,
                    event_type VARCHAR(10),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id VARCHAR(255),
                    product_id VARCHAR(255)
                );
            """)
        self.conn.commit()