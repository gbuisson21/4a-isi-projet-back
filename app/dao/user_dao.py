from fastapi import HTTPException
from sqlmodel import select, Session

from app.models import Product, ProductPublic

from app.models import User, UserRegister, UserAuth


class UserDao:
    def __init__(self, session: Session):
        self.session = session

    def get_user_by_mail(self, mail:str) -> UserAuth| None:
        query = select(UserAuth).where(UserAuth.mail == mail)
        user = self.session.exec(query).first()
        
        return user


    def create_user(self, userRegister : UserRegister):
        if not self.get_user_by_mail(userRegister.mail):
            user = User(name=userRegister.name , admin=False, locked=False)
            self.session.add(user)
            self.session.commit()
            
            userAuth = UserAuth()

            if not user.id : 
                raise HTTPException(status_code=500, detail="Internal Error !")
            
            userAuth.id = user.id
            userAuth.mail = userRegister.mail
            userAuth.password = userRegister.password

            self.session.add(userAuth)
            self.session.commit()

            return user

        else: 
            raise HTTPException(status_code=409, detail="Email already used !")


        
    