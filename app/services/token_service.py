from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from jwt import InvalidTokenError
from starlette import status

from app.models import User, TokenData, oauth2_scheme
import os
import datetime


class TokenService:
    def __init__(self) -> None:
        self.__secret = os.environ['SECRETJWT']
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = datetime.timedelta(minutes=20)

    def create_token(self, user: User):
        to_encode = user.user_token_data()

        expire = datetime.datetime.now(datetime.timezone.utc) + self.ACCESS_TOKEN_EXPIRE_MINUTES

        to_encode.update({ "exp": expire})

        encoded_jwt = jwt.encode(to_encode, self.__secret, algorithm=self.ALGORITHM)
        return encoded_jwt

    @classmethod
    def is_admin(cls, token: TokenData):
        return token.admin


    def decode_access_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, self.__secret, algorithms=[self.ALGORITHM])
        except jwt.PyJWTError as exc:
            raise InvalidTokenError() from exc


    def parse_token(self, token: str) -> TokenData:
        payload = self.decode_access_token(token)
        try:
            username = payload.get("sub")
            user_id = payload.get("id")
            admin = payload.get("admin")
            locked = payload.get("locked")
            return TokenData(id=user_id, name=username, admin=admin, locked=locked)
        except (KeyError, ValueError):
            raise InvalidTokenError()


    def get_current_user(self, token: Annotated[str, Depends(oauth2_scheme)]):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            token_data = self.parse_token(token)
        except InvalidTokenError:
            raise credentials_exception
        return User(name=token_data.name, admin=token_data.admin, locked=token_data.locked)
