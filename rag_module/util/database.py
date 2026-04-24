from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv(override=True)

engine = create_engine(os.getenv("db_connection_string"))

Session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Model = declarative_base()