from app.dao.user_dao import UserDao
from app.models import UserRegister, UserLogin, User
from app.services.token_service import TokenService
from fastapi import HTTPException
from app.services.hash_service import HashService

class UserService:
    def __init__(self, dao : UserDao, tokenService : TokenService, hashService : HashService) -> None:
        self.dao = dao
        self.tokenService = tokenService
        self.hashService = hashService
       

    def register(self, userRegister : UserRegister):
        user = self.dao.create_user(userRegister)

        return self.tokenService.create_token(user)


    def login(self, userLogin : UserLogin):
        userAuth = self.dao.get_user_by_mail(userLogin.mail)
        if not userAuth:
            #user existe pas 
            raise HTTPException(status_code=401, detail="Mail or password incorrect !")


        same = self.hashService.check_hash(userLogin.password, userAuth.password_hash)

        if not same:
            raise HTTPException(status_code=401, detail="Mail or password incorrect !")

        if userAuth.id:
            user = self.dao.get_user_by_id(userAuth.id)
            if user:
                return self.tokenService.create_token(user)

