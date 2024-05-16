from datetime import timedelta
import os

# jwt配置
SECRET_KEY = "fed8a19950e4065ff34e8d12f0657ca36dbb8cdca36b5a14c3b6cc5d65a52103"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = timedelta(minutes=999999999)

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./data.sqlite"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

PHOTOPATH = os.path.join(os.path.expanduser('~'),'Downloads','beauty')

GRADEPATH = 'grade'