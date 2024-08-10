import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text

db = SQLAlchemy()

import logging
import colorlog

# Initialize logging with colorlog
log_colors = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}

formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)s:%(name)s:%(message)s (%(filename)s:%(lineno)d)",
    log_colors=log_colors
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the logging level
logger.addHandler(handler)
logger.propagate = False  # Disable propagation to avoid duplicate log messages

def init_db(app):
    db.init_app(app)

def create_tables(app):
    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()

        # Create all tables
        db.create_all()
        logger.info("Created tables: events, wikipediaPages, wikiTraffic")
        tables_to_clear = ['events', 'wikipediaPages', 'wikiTraffic']
        for table in tables_to_clear:
            if table in existing_tables:
                logger.info(f"Clearing table: {table}")
                db.session.execute(text(f"DELETE FROM {table}"))
            else:
                logger.info(f"Table {table} does not exist, skipping.")

        db.session.commit()
        logger.info("Tables cleared: events, wikipediaPages, wikiTraffic")

def print_all_tables(app):
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        logger.info("*****************************************************")
        logger.info("***** Printing all tables and their columns *********")
        logger.info("*****************************************************")

        for table in tables:
            columns = [column['name'] for column in inspector.get_columns(table)]
            logger.info(f"- {table}, columns: {', '.join(columns)}")

        logger.info("*****************************************************")
        logger.info("*****************************************************\n\n")