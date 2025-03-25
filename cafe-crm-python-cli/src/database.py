from sqlalchemy import create_engine, MetaData
from sqlalchemy import select, insert, update, delete, text
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DB_URL')

if not db_url:
    raise ValueError("Database URL is missing!")


# engine = create_engine("mysql+pymysql://root:tars@localhost/cafe_crm")
engine = create_engine(db_url)
metadata = MetaData()

metadata.reflect(bind=engine)
tables = metadata.tables.keys()
