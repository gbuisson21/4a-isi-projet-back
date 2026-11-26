from fastapi import APIRouter, Depends, HTTPException


from app.database import db
from app.models import UserRegister, UserLogin

from email_validator import EmailNotValidError, validate_email

from app.dependency import UserServiceDep


router = APIRouter(prefix="/api", tags=["public"])



@router.post("/user/register")
def create_user(user_register : UserRegister, service  : UserServiceDep):
    try:
        info = validate_email(user_register.mail)

    except EmailNotValidError as e:
        raise HTTPException(status_code=417, detail="Bad Email")

    if len(user_register.name) < 1:
        raise HTTPException(status_code=417, detail="Name too short")

    if len(user_register.password) < 8:
            raise HTTPException(status_code=417, detail="Password too short")

    return service.register(user_register)

@router.post("/user/login")
def login_user(user_login : UserLogin, service  : UserServiceDep):
    try:
        info = validate_email(user_login.mail)

    except EmailNotValidError as e:
        raise HTTPException(status_code=417, detail="Bad Email")

    return service.login(user_login)
