from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt

from config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM

# 加密上下文，用于验证密码
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 验证密码
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# 创建JWT令牌
def create_access_token(data: dict, expires_delta: timedelta = ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 解析JWT令牌
def decode_access_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)

# 解析jwt令牌 不验证签名
def decode_access_token_without_verification(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM, options={"verify_signature": False})