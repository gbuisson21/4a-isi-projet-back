from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import db
from app.dependency import ProductServiceDep
from app.models import Product, ProductPublic
from app.models import UserRegister

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


