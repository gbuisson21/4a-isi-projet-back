import jwt 
from app.models import User
import os
import datetime



class TokenService:
    def __init__(self) -> None:
        self.__secret = os.environ['SECRETJWT']
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = datetime.timedelta(minutes=20)


    def create_token(self, user : User):
        to_encode = user.data()

        expire = datetime.datetime.now(datetime.timezone.utc) + self.ACCESS_TOKEN_EXPIRE_MINUTES

        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(to_encode, self.__secret, algorithm=self.ALGORITHM)
        return encoded_jwt
       


