from fastapi import HTTPException
from datetime import datetime, UTC
from . import models, schemas
from sqlalchemy.orm import Session, Query
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_tests_by_user_email(db: Session, email: str):
    # Выбираем только id, test_metadata и owner_email
    return db.query(
        models.Test.id,
        models.Test.test_metadata,
        models.Test.owner_email
    ).filter(
        models.Test.owner_email == email
    ).all()


def save_test(db: Session, test: models.Test):
    db.add(test)
    db.commit()
    db.refresh(test)


def get_test_by_test_id(db: Session, test_id: str):
    test = db.query(models.Test).filter(models.Test.id == test_id).first()

    if not test:
        raise HTTPException(status_code=404, detail='Test not found')

    return test


def delete_test_by_test_id(db: Session, test_id: str):
    test = db.query(models.Test).filter(models.Test.id == test_id).first()

    if not test:
        raise HTTPException(status_code=404, detail='Test not found')

    db.delete(test)
    db.commit()

def update_test_by_id(db: Session, test_id, updated_test):
    db_test = db.query(models.Test).filter(models.Test.id == test_id).first()

    if not db_test:
        raise HTTPException(status_code=404, detail="Test not found")

    # 2. Обновляем поля
    if updated_test.title is not None:
        db_test.test_metadata["title"] = updated_test.title

    if updated_test.questions is not None:
        # Преобразуем вопросы в словари, если нужно
        db_test.content = [q.dict() for q in updated_test.questions]
        db_test.test_metadata["questions_count"] = len(updated_test.questions)

    # Обновляем метаданные
    db_test.test_metadata["updated_at"] = datetime.now(UTC).isoformat()

    # 3. Сохраняем изменения
    db.commit()
    db.refresh(db_test)
