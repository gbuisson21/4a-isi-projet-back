from fastapi import HTTPException
from sqlmodel import select, Session

from app.models import Product, ProductPublic

from app.models import User, UserRegister, UserAuth

from app.services.hash_service import HashService


class UserDao:
    def __init__(self, session: Session, hashService : HashService):
        self.session = session
        self.hashService = hashService

    def get_user_by_mail(self, username :str) -> UserAuth| None:
        query = select(UserAuth).where(UserAuth.username == username)
        user = self.session.exec(query).first()
        
        return user

    def get_user_by_id(self, id :int) -> User | None:
        query = select(User).where(User.id == id)
        user = self.session.exec(query).first()
        
        return user


    def create_user(self, userRegister : UserRegister):
        if not self.get_user_by_mail(userRegister.mail):
            user = User(name=userRegister.name , admin=False, locked=False)
            self.session.add(user)
            self.session.commit()
            
            userAuth = UserAuth(id=user.id, username = userRegister.mail, password_hash =self.hashService.hash(userRegister.password))

            if not user.id : 
                raise HTTPException(status_code=500, detail="Internal Error !")

            self.session.add(userAuth)
            self.session.commit()

            return user

        else: 
            raise HTTPException(status_code=409, detail="Email already used !")


        
    