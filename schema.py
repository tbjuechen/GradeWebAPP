from pydantic import BaseModel
from datetime import datetime


class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserLogin(UserBase):
    password: str

class UserInDB(UserBase):
    id: int

    class Config:
        orm_mode = True

class PhotoInDB(BaseModel):
    id: int
    name: str
    location: str

    class Config:
        orm_mode = True

class GradeMessage(BaseModel):
    photo_id:int
    grade:int
    is_nagative:bool

# 定义 AccessToken 模型
class AccessToken(BaseModel):
    access_token: str  # JWT 令牌
    token_type: str  # 令牌类型，例如 "bearer"

class PhotoBase(BaseModel):
    id: int

class PhotoCreate(BaseModel):
    name: str
    location: str

class PhotoInDB(PhotoBase):
    name: str
    location: str

    class Config:
        orm_mode = True

class GradeBase(BaseModel):
    user_id: int
    photo_id: int
    grade: int

class GradeCreate(GradeBase):
    create_at: datetime

class GradeInDB(GradeBase):
    create_at: datetime

    class Config:
        orm_mode = True

class RankItem(BaseModel):
    rank: int 
    username: str
    count: int

class NagativeInfo(BaseModel):
    total: int
    nagative: int

class Gradeinfo(BaseModel):
    grade: list[int]
    average: float

class PhotoGrade(BaseModel):
    rank: int
    photo_id: int
    ave_grade: float

class RequestRange(BaseModel):
    start: int
    end: int

class UserGradeRecord(BaseModel):
    username : str
    grade : int
    create_at : datetime