import os
import dotenv
from sqlalchemy import create_engine
import sqlalchemy

def database_connection_url():
    dotenv.load_dotenv()

    return os.environ.get("POSTGRES_URI")

engine = create_engine(database_connection_url(), pool_pre_ping=True)

metadata_obj = sqlalchemy.MetaData()
purchases = sqlalchemy.Table("customer_purchases", metadata_obj, autoload_with=engine)