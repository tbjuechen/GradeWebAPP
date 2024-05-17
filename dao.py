from sqlalchemy import func, case,and_
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Union

from model import User,Photo,Grade
from schema import UserCreate, PhotoCreate, GradeCreate, NagativeInfo


# 根据id获取用户
async def get_uset_by_id(db: Session, user_id: int) -> Union[User, None]:
    return db.query(User).filter(User.id == user_id).first()

# 根据用户名获取用户
async def get_user_by_username(db: Session, username: str) -> Union[User, None]:
    return db.query(User).filter(User.username == username).first()

# 创建用户
async def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(username=user.username, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 创建照片
async def create_photo(db: Session, photo: PhotoCreate) -> Photo:
    db_photo = Photo(name=photo.name, location=photo.location)
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo

# 根据id获取照片
async def get_photo_by_id(db: Session, photo_id: int) -> Union[Photo, None]:
    return db.query(Photo).filter(Photo.id == photo_id).first()

# 获取照片id范围
async def get_photo_id_range(db: Session) -> Union[int, None]:
    return db.query(Photo).count()

# 创建评分
async def create_grade(db: Session, user_id: int, photo_id: int, grade: int) -> Grade:
    db_grade = Grade(user_id=user_id, photo_id=photo_id, grade=grade, create_at=datetime.utcnow())
    db.add(db_grade)
    db.commit()
    db.refresh(db_grade)
    return db_grade

# 统计每个人的打分次数 输出为(username,count) 的列表
async def count_grade_times(db: Session) -> dict:
    return db.query(User.username, func.count(Grade.id)).join(Grade).group_by(User.username).order_by(func.count(Grade.id).desc()).all()

# 统计grade表中的总记录数和grade=-1的记录数
async def count_grade(db: Session) -> NagativeInfo:
    total = db.query(Grade).count()
    nagative = db.query(Grade).filter(Grade.grade == -1).count()
    return NagativeInfo(total=total, nagative=nagative)

# 统计grade表中指定用户的总记录数和grade=-1的记录数
async def count_grade_by_user(db: Session, user_id: int) -> NagativeInfo:
    total = db.query(Grade).filter(Grade.user_id == user_id).count()
    nagative = db.query(Grade).filter(Grade.user_id == user_id, Grade.grade == -1).count()
    return NagativeInfo(total=total, nagative=nagative)

# 统计某个用户不同分值的打分次数
async def count_grade_by_user_and_grade(db: Session, user_id: int):
    return db.query(Grade.grade, func.count(Grade.id)).filter(Grade.user_id == user_id).group_by(Grade.grade).all()

# 统计每有评分的照片剔除-1的平均分并从高到低排序
async def count_average_grade(db: Session):
    return db.query(Grade.photo_id, func.avg(Grade.grade)).filter(Grade.grade != -1).group_by(Grade.photo_id).order_by(func.avg(Grade.grade).desc()).all()

# 统计每张至少有2个评分 且-1的评分数目小于一半的照片，剔除-1的平均分并从高到低排序
async def count_average_grade_v2(db: Session):
    subquery = (
        db.query(
            Grade.photo_id,
            func.count(Grade.id).label('total_grades'),
            func.sum(case((Grade.grade == -1, 1), else_=0)).label('negative_grades'),
            func.avg(case((Grade.grade != -1, Grade.grade), else_=None)).label('average_grade')
        )
        .group_by(Grade.photo_id)
        .having(and_(
            func.count(Grade.id) >= 2,
            func.sum(case((Grade.grade == -1, 1), else_=0)) < (func.count(Grade.id) / 2)
        ))
        .subquery()
    )

    # 排序并查询结果
    query = (
        db.query(
            Photo.id,
            subquery.c.average_grade
        )
        .join(subquery, Photo.id == subquery.c.photo_id)
        .order_by(subquery.c.average_grade.desc())
    )

    results = query.all()
    return results
    

# 根据photo_id获取照片的评分数据,其中包含rank,user.username,grade,create_at
async def get_grade_by_photo_id(db: Session, photo_id: int):
    return db.query(User.username, Grade.grade, Grade.create_at).join(Grade).filter(Grade.photo_id == photo_id).all()