import jwt 
from app.models import User
import os
import datetime
from app.dao.user_dao import UserDao
from app.models import UserRegister
from app.services.token_service import TokenService


class UserService:
    def __init__(self, dao : UserDao, tokenService : TokenService) -> None:
        self.dao = dao
        self.tokenService = tokenService
       

    def register(self, userRegister : UserRegister):
        user = self.dao.create_user(userRegister)

        
        return self.tokenService.create_token(user)
     