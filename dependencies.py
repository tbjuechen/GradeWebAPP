from config import SessionLocal

# 返回数据库连接
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from fastapi import Depends, HTTPException, status, Path
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Union
import jwt

from auth_util import decode_access_token, decode_access_token_without_verification
from dao import get_user_by_username
from model import User
import dao

# 依赖项，用于从请求中获取令牌
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# 获取当前用户
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") 
    # token 过期
    except jwt.ExpiredSignatureError:
        username = decode_access_token_without_verification(token).get("sub")
        user = await get_user_by_username(db, username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    # token 无效
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user: Union[User, None] = await get_user_by_username(db, username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

# 通过路径变量获取照片
async def get_target_photo(photo_id: str = Path(...), db: Session = Depends(get_db)):
    photo = await dao.get_photo_by_id(db, int(photo_id))
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    return photo