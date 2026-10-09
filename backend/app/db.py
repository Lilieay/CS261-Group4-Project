from sqlalchemy import create_engine
from sqlalchemy.engine import URL

from .config import DB_CONNECTION_STRING


connection_url = URL.create(
    "mssql+pyodbc",
    query={"odbc_connect": DB_CONNECTION_STRING},
)

engine = create_engine(connection_url, pool_pre_ping=True)