from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException , Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from ..database import SessionLocal
from ..models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm , OAuth2PasswordBearer
from jose import jwt , JWTError
from fastapi.templating import Jinja2Templates
from fastapi import Form
from fastapi.responses import RedirectResponse

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


SECRET_KEY = '2d5156abfbd1534fcd788284e0e9283f4ca3e7f70e016df22789fd3ef5d45f1f'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str

class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

db_dependency = Annotated[Session, Depends(get_db)]

templates = Jinja2Templates(directory="TodoApp/templates")

#### Paginas ###
@router.get("/login-page")
def render_login_page(request:Request):
    return templates.TemplateResponse("login.html", {"request": request})
@router.get("/register-page")
def render_register_page(request:Request):
    return templates.TemplateResponse("register.html", {"request": request})



### Enndpoints ###

def authenticate_users(username: str, password: str,db):
    user =db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int , role: str , expires_delta: timedelta):

    encode = {'sub': username , 'id': user_id, 'role': role}
    expires= datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("sub") is None or payload.get("id") is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user."
            )

        return {
            "username": payload.get("sub"),
            "user_id": payload.get("id"),
            "user_role": payload.get("role"),
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user."
        )

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    email: str = Form(...),
    username: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    phone_number: str = Form(...),
    db: Session = Depends(get_db),
):
    create_user_model = Users(
        email=email,
        username=username,
        first_name=first_name,
        last_name=last_name,
        role=role,
        hashed_password=bcrypt_context.hash(password),
        phone_number=phone_number,
        is_active=True,
    )

    db.add(create_user_model)
    db.commit()

    return RedirectResponse(
        url="/auth/login-page",
        status_code=status.HTTP_302_FOUND
    )

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user= authenticate_users(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
    token= create_access_token(user.username, user.id , user.role,  timedelta(minutes=20))

    return {'access_token': token, 'token_type': 'bearer'}

@router.post("/login")
async def login_web(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = authenticate_users(username, password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token(
        user.username,
        user.id,
        user.role,
        timedelta(minutes=20)
    )

    response = RedirectResponse(
        url="/todos/todo-page",
        status_code=status.HTTP_302_FOUND
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
    )

    return response

