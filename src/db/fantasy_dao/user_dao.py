from typing import Optional
from sqlalchemy.orm import Session
from src.common.schemas.fantasy_schemas import User, UserID
from src.db.models import UserModel


def create_user(session: Session, user: User) -> None:
    db_user = UserModel(**user.model_dump())
    session.add(db_user)
    session.commit()


def get_user_by_id(session: Session, user_id: UserID) -> Optional[User]:
    user_model: Optional[UserModel] = session.query(UserModel)\
        .filter(UserModel.id == user_id)\
        .first()
    if user_model is None:
        return None
    else:
        return User.model_validate(user_model)


def get_user_by_username(session: Session, username: str) -> Optional[User]:
    user_model: Optional[UserModel] = session.query(UserModel)\
        .filter(UserModel.username == username)\
        .first()
    if user_model is None:
        return None
    else:
        return User.model_validate(user_model)


def get_user_by_email(session: Session, email: str) -> Optional[User]:
    user_model: Optional[UserModel] = session.query(UserModel)\
        .filter(UserModel.email == email)\
        .first()
    if user_model is None:
        return None
    else:
        return User.model_validate(user_model)
