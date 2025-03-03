from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def password_hasher(password: str):
    return pwd_context.hash(password)
