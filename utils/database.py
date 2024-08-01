import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)

def create_tables(app):
    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()

        # Create all tables
        db.create_all()
        print("Created tables: events, wikipediaPages, wikiTraffic")

        if os.environ.get('DELETE_DATABASES', 'False').lower() == 'true':
            print("Resetting tables...")

            tables_to_clear = ['events', 'wikipediaPages', 'wikiTraffic']
            for table in tables_to_clear:
                if table in existing_tables:
                    print(f"Clearing table: {table}")
                    db.session.execute(text(f"DELETE FROM {table}"))
                else:
                    print(f"Table {table} does not exist, skipping.")

            db.session.commit()
            print("Tables cleared: events, wikipediaPages, wikiTraffic")

def print_all_tables(app):
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print("Tables in the database:")
        for table in tables:
            columns = [column['name'] for column in inspector.get_columns(table)]
            print(f"- {table}, columns: {', '.join(columns)}")
