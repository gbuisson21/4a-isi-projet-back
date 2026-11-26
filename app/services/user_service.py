from app.dao.user_dao import UserDao
from app.models import UserRegister, UserLogin, User
from app.services.token_service import TokenService
from fastapi import HTTPException
from app.services.hash_service import HashService

class UserService:
    def __init__(self, dao : UserDao, token_service : TokenService, hash_service : HashService) -> None:
        self.dao = dao
        self.token_service = token_service
        self.hash_service = hash_service
       

    def register(self, user_register : UserRegister):
        password_hash = self.hash_service.hash(user_register.password)
        user = self.dao.create_user(user_register, password_hash)
        
        return self.token_service.create_token(user)


    def login(self, user_login : UserLogin):
        user_auth = self.dao.get_user_by_mail(user_login.mail)
        if not user_auth:
            #user existe pas 
            raise HTTPException(status_code=401, detail="Mail or password incorrect !")


        same = self.hash_service.check_hash(user_login.password, user_auth.password_hash)

        if not same:
            raise HTTPException(status_code=401, detail="Mail or password incorrect !")

        if user_auth.id:
            user = self.dao.get_user_by_id(user_auth.id)
            if user:
                return self.token_service.create_token(user)

