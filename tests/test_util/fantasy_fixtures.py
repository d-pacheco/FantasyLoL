import uuid
import bcrypt

from fantasylol.schemas import fantasy_schemas

user_password = "WeakTestPw"
salt = bcrypt.gensalt()
user_hashed_password = bcrypt.hashpw(str.encode(user_password), salt)

user_create_fixture = fantasy_schemas.UserCreate(
    username="MyUsername",
    email="MyEmail@gmail.com",
    password=user_password
)

user_fixture = fantasy_schemas.User(
    id=str(uuid.uuid4()),
    username=user_create_fixture.username,
    email=user_create_fixture.email,
    password=user_hashed_password
)
