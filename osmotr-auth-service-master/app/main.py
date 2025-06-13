from datetime import datetime, UTC
import uuid

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from . import models, schemas, crud, auth, database
from .database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
origins = [
    "http://localhost",  # Адрес вашего фронтенда
    "null"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db=Depends(database.get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user)


@app.post("/auth")
def auth_func(user: schemas.UserCreate, db=Depends(database.get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if not db_user:
        raise HTTPException(status_code=400, detail="User not registered")
    access_token = auth.create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}



@app.post("/verify", response_model=schemas.User)
def read_current_user(token: str = Depends(oauth2_scheme), db=Depends(database.get_db)):
    user = auth.get_current_user(db, token)
    return user


@app.get('/tests', response_model=schemas.TestsResponse)
def get_user_tests(
        token: str = Depends(oauth2_scheme),
        db=Depends(database.get_db)
):
    user = auth.get_current_user(db, token)
    # Получаем только метаданные тестов
    tests = crud.get_tests_by_user_email(db, email=user.email)

    # Преобразуем в список словарей (если нужно)
    tests_data = [
        {
            "id": t.id,
            "test_metadata": t.test_metadata,
            "owner_email": t.owner_email
        }
        for t in tests
    ]

    return {"tests": tests_data}

@app.post('/tests')
def upload_test(
        test: schemas.SaveTest,
        token: str = Depends(oauth2_scheme),
        db=Depends(database.get_db)
):
    user = auth.get_current_user(db, token)
    test_id = f'{user.email}_'+str(uuid.uuid4())
    test_metadata = {
        'test_id': test_id,
        'title': test.title,
        'created_at': datetime.now(UTC).isoformat(),
        'updated_at': datetime.now(UTC).isoformat(),
        'questions_count': len(test.questions)
    }

    # Преобразуем вопросы в словари
    questions_data = [q.model_dump() for q in test.questions]

    test_db = models.Test(
        id=test_id,
        test_metadata=test_metadata,
        content=questions_data,  # Теперь это список словарей, а не объектов QuestionItem
        owner_email=user.email
    )

    crud.save_test(db, test_db)
    return {'detail': 'Test is saved'}

@app.delete('/tests/{test_id}')
def delete_test(
        test_id: str,
        db = Depends(database.get_db)
                ):
    crud.delete_test_by_test_id(db, test_id)
    return {"detail": "test deleted succesfully"}

@app.get('/tests/{test_id}', response_model=schemas.SaveTest)
def get_test_for_edit(
        test_id: str,
        db = Depends(database.get_db)
                ):
    test_from_db = crud.get_test_by_test_id(db, test_id)

    test_response = schemas.SaveTest(
        title=test_from_db.test_metadata['title'],
        questions = test_from_db.content
    )
    return test_response

@app.put('/tests/{test_id}')
def get_test_for_edit(
        test_id: str,
        updated_test: schemas.SaveTest,
        db = Depends(database.get_db)
                ):
    crud.update_test_by_id(db, test_id, updated_test)

    return {'detail': 'test succesfully updated'}