from sqlalchemy.orm import Session
from fastapi import HTTPException, status

import random

import schema
from model import User
from auth_util import pwd_context, verify_password, create_access_token
import dao

# 创建用户
async def create_user(db: Session, user: schema.UserCreate):
    # 检查用户名是否唯一
    existing_user = await dao.get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    
    user.password = pwd_context.hash(user.password)
    db_user = await dao.create_user(db, user)
    return db_user

# 用户登录
async def authenticate_user(db: Session, user: schema.UserLogin):
    password = user.password
    user = await dao.get_user_by_username(db, user.username)
    # 用户不存在
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # 密码错误
    if not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")
    # 生成并返回 JWT 令牌
    access_token = create_access_token(data={"sub": user.username})
    return access_token

# 返回随机照片
async def get_random_photo(db: Session):
    photo_id_range = await dao.get_photo_id_range(db)
    if photo_id_range == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No photo found")
    photo_id = random.randint(1, photo_id_range)
    photo = await dao.get_photo_by_id(db, photo_id)
    return photo
