import argparse

from pydantic import validate_email
from sqlmodel import select

from app.database import db
from app.dependency import get_hash_service
from app.models import User, UserAuth


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", help="username", required=True)
    parser.add_argument("-p", help="password", required=True)
    parser.add_argument("-e", help="Email", required=True)
    args = parser.parse_args()

    password_service = get_hash_service()

    username = args.u

    email = args.e
    validate_email(email)

    password_hash = password_service.hash(args.p)

    session_gen = db.get_session()
    session = next(session_gen)

    try:
        query = select(UserAuth).where(UserAuth.username == email)
        result = session.exec(query).first()

        if result:
            raise ValueError("User already exists !")

        user = User(name=username, admin=True, locked=False)
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("Missing id !")

        user_auth = UserAuth(id=user.id, username=email, password_hash=password_hash)
        session.add(user_auth)
        session.commit()

        print("User created !")
    finally:
        session_gen.close()


if __name__ == "__main__":
    main()