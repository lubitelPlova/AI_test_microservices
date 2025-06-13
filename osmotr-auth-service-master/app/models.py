from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship
import uuid
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    tests = relationship("Test", back_populates="owner")

class Test(Base):
    __tablename__ = 'tests'

    # Для SQLite используем String вместо UUID (не все версии SQLite поддерживают UUID)
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    test_metadata = Column(JSON, nullable=False)  # SQLite будет хранить как TEXT с JSON
    content = Column(JSON, nullable=False)
    # Добавляем внешний ключ на email пользователя
    owner_email = Column(String, ForeignKey("users.email"), nullable=False)

    # Добавляем связь с пользователем
    owner = relationship("User", back_populates="tests")

    def __repr__(self):
        return f"<Test(id={self.id}, title={self.metadata.get('title')})>"