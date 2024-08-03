
from sqlalchemy import Table, Column, Date, Float, MetaData
from utils.database import db

class WikiTrafficRepository:
    def __init__(self):
        self.metadata = MetaData()
        self.table = None

    def create_table(self, columns):
        table_columns = [
            Column('date', Date, primary_key=True)
        ]
        for column in columns:
            if column != 'date':
                table_columns.append(Column(column, Float))

        self.table = Table('wikiTraffic', self.metadata, *table_columns, extend_existing=True)
        self.metadata.create_all(db.engine)


    def insert_or_update(self, date, row_data):
        if self.table is None:
            raise Exception("Table not created. Call create_table first.")

        existing_columns = set(self.get_all_columns())
        filtered_data = {k: v for k, v in row_data.items() if k in existing_columns}
        filtered_data['date'] = date

        existing = db.session.query(self.table).filter(self.table.c.date == date).first()
        if existing:
            db.session.query(self.table).filter(self.table.c.date == date).update(filtered_data)
        else:
            db.session.execute(self.table.insert().values(**filtered_data))

    def commit(self):
        db.session.commit()

    def get_all_columns(self):
        if self.table is None:
            self.table = Table('wikiTraffic', self.metadata, autoload_with=db.engine)
        return [c.name for c in self.table.columns]

    def get_all(self):
        if self.table is None:
            self.table = Table('wikiTraffic', self.metadata, autoload_with=db.engine)
        return db.session.query(self.table).all()

    def get_by_date(self, date):
        if self.table is None:
            self.table = Table('wikiTraffic', self.metadata, autoload_with=db.engine)
        return db.session.query(self.table).filter(self.table.c.date == date).first()
