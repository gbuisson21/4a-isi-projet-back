from fastapi import HTTPException
from sqlmodel import select, Session

from app.models import Product, ProductPublic

from app.models import User, UserRegister, UserAuth


class UserDao:
    def __init__(self, session: Session):
        self.session = session

    def create_user(self, userRegister : UserRegister):
        user = User(name=userRegister.name , admin=False, locked=False)
        self.session.add(user)
        self.session.commit()
        
        userAuth = UserAuth(id=user.id, mail = userRegister.mail, password=userRegister.password)

        self.session.add(userAuth)
        self.session.commit()

        return user
    