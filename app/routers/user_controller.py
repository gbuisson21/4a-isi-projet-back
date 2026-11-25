from fastapi import APIRouter, Depends, HTTPException


from app.database import db
from app.models import UserRegister, UserLogin

from email_validator import EmailNotValidError, validate_email

from app.dependency import UserServiceDep


router = APIRouter(prefix="/api", tags=["public"])



@router.post("/users/")
def create_user(userRegister : UserRegister, service  : UserServiceDep):
    try:
        info = validate_email(userRegister.mail)

    except EmailNotValidError as e:
        raise HTTPException(status_code=417, detail="Bad Email")

    if len(userRegister.name) < 1:
        raise HTTPException(status_code=417, detail="Name too short")

    if len(userRegister.password) < 8:
            raise HTTPException(status_code=417, detail="Password too short")

    return service.register(userRegister)

@router.post("/user/")
def login_user(userLogin : UserLogin, service  : UserServiceDep):
    try:
        info = validate_email(userLogin.mail)

    except EmailNotValidError as e:
        raise HTTPException(status_code=417, detail="Bad Email")

    return service.login(userLogin)
