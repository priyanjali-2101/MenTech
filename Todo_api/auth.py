
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Table ,create_engine
from sqlalchemy.orm import sessionmaker, relationship
from database import Base 
from sqlalchemy.ext.declarative import declarative_base


SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args ={'check_same_thread':'False'})

SESSION_LOCAL = sessionmaker(bind=engine, autucommit=False, autoflush= False)

Base = declarative_base()

# user table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True,)
    name = Column(String, nullable=False)

    roles = relationship(
        'Role',
        secondary=association_table, back_populates="students"
    )