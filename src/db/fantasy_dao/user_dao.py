from sqlalchemy.orm import Session
from src.common.schemas.fantasy_schemas import User, UserID, UserAccountStatus
from src.db.models import UserModel


def create_user(session: Session, user: User) -> None:
    db_user = UserModel(**user.model_dump())
    session.add(db_user)
    session.commit()


def get_user_by_id(session: Session, user_id: UserID) -> User | None:
    db_user: UserModel | None = session.query(UserModel)\
        .filter(UserModel.id == user_id)\
        .first()
    if db_user is None:
        return None
    else:
        return User.model_validate(db_user)


def get_user_by_username(session: Session, username: str) -> User | None:
    db_user: UserModel | None = session.query(UserModel)\
        .filter(UserModel.username == username)\
        .first()
    if db_user is None:
        return None
    else:
        return User.model_validate(db_user)


def get_user_by_email(session: Session, email: str) -> User | None:
    db_user: UserModel | None = session.query(UserModel)\
        .filter(UserModel.email == email)\
        .first()
    if db_user is None:
        return None
    else:
        return User.model_validate(db_user)


def update_user_account_status(
        session: Session,
        user_id: UserID,
        account_status: UserAccountStatus
) -> None:
    db_user: UserModel | None = session.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user:
        db_user.account_status = account_status
        session.merge(db_user)
        session.commit()


def update_user_verified(session: Session, user_id: UserID, verified: bool) -> None:
    db_user: UserModel | None = session.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user:
        db_user.verified = verified
        session.merge(db_user)
        session.commit()


def get_user_by_verification_token(session: Session, verification_token: str) -> User | None:
    db_user: UserModel | None = session.query(UserModel)\
        .filter(UserModel.verification_token == verification_token).first()
    if db_user is None:
        return None
    else:
        return User.model_validate(db_user)


def update_user_verification_token(
        session: Session,
        user_id: UserID,
        verification_token: str | None
) -> None:
    db_user: UserModel | None = session.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user:
        db_user.verification_token = verification_token
        session.merge(db_user)
        session.commit()
