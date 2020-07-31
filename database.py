from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = create_engine("postgres://postgres@/VKinterdb")
Session = sessionmaker(bind=engine)
session = Session()

class Allopenedusers(Base):
    __tablename__ = 'allopenedusers'

    id = Column(Integer, primary_key=True)
    sex = Column(Integer, nullable=False)
    bdate = Column(Date) # ПОЧИТАТЬ КАК ДАТУ ПЕРЕДАТЬ ПРАВИЛЬНО
    city = Column(JSONB, nullable=True)
    country = Column(JSONB, nullable=True)
    verified = Column(Integer)
    first_name = Column(String(20))
    last_name = Column(String(20))
    nickname = Column(String(30))
    occupation = Column(JSONB, nullable=True)
    interests = Column(String(300))
    books  = Column(String(100))
    activities = Column(String(300))
    has_photo = Column(Integer, nullable=False)
    common_count = Column(Integer, nullable=False)
    is_friend = Column(Integer, nullable=False)
