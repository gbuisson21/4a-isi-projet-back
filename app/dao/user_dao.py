from fastapi import HTTPException
from sqlmodel import select, Session


from app.models import User, UserRegister, UserAuth



class UserDao:
    def __init__(self, session: Session):
        self.session = session

    def get_user_by_mail(self, username :str) -> UserAuth| None:
        query = select(UserAuth).where(UserAuth.username == username)
        user = self.session.exec(query).first()
        
        return user

    def get_user_by_id(self, id :int) -> User | None:
        query = select(User).where(User.id == id)
        user = self.session.exec(query).first()
        
        return user


    def create_user(self, user_register : UserRegister, password_hash : str):
        if not self.get_user_by_mail(user_register.mail):
            user = User(name=user_register.name , admin=False, locked=False)
            self.session.add(user)
            self.session.commit()
            
            user_auth = UserAuth(id=user.id, username = user_register.mail, password_hash =password_hash)

            if not user.id : 
                raise HTTPException(status_code=500, detail="Internal Error !")

            self.session.add(user_auth)
            self.session.commit()

            return user

        else: 
            raise HTTPException(status_code=409, detail="Email already used !")


        
    