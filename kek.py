from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)  # Добавьте эту строку, чтобы включить столбец hashed_password

# Предполагая, что вы уже определили модель User с столбцом hashed_password

engine = create_engine('sqlite:///users.db')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Пересоздание схемы базы данных
Base.metadata.create_all(bind=engine)