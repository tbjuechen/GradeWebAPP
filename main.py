from fastapi import FastAPI, Response, Query, Path,HTTPException,status,Body,Depends
import os
import random
import shutil
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from config import Base,engine,PHOTOPATH,GRADEPATH
from model import User,Photo,Grade
from schema import GradeMessage,PhotoInDB,AccessToken,UserLogin,UserCreate,\
    UserInDB,RankItem,NagativeInfo,PhotoGrade,RequestRange,GradeInDB,UserGradeRecord
from dependencies import get_db,get_current_user,get_target_photo
import service
import dao

from dependencies import oauth2_scheme


app = FastAPI(openapi_prefix="/api")


def choose_random_file(directory):
    file_list = os.listdir(directory)
    random_file = random.choice(file_list)
    return random_file

@app.get('/photo/{photo_id}')
def push_photo(photo:Photo = Depends(get_target_photo)):
    photo_path = photo.location
    if os.path.exists(photo_path):
        with open(photo_path,'rb') as f:
            img = f.read()
            return Response(content=img, media_type="image/jpeg")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='photo not found!')
    
@app.get('/photoinfo',response_model=PhotoInDB)
async def grade_init(db: Session = Depends(get_db)):
    photo = await service.get_random_photo(db)
    return photo

@app.post('/grade/{photo_id}')
async def grade(photo:Photo = Depends(get_target_photo), user:UserInDB = Depends(get_current_user), gradeinfo:GradeMessage = Body(...), db: Session = Depends(get_db)):
    if gradeinfo.is_nagative:
        grade = -1
    else:
        grade = gradeinfo.grade
    await dao.create_grade(db,user.id,photo.id,grade)
    return {"message":"grade success!"}
        

@app.post("/login", response_model= AccessToken, tags=["user"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user : UserLogin = UserLogin(username=form_data.username, password=form_data.password)
    access_token = await service.authenticate_user(db, user)
    return AccessToken(access_token=access_token, token_type="bearer")

@app.post("/register", response_model=UserInDB, tags=["user"])
async def register(user: UserCreate, db: Session = Depends(get_db)):
    return await service.create_user(db, user)  

@app.get('/getuser',response_model=UserInDB, tags=["user"])
async def get_user(user:UserInDB = Depends(get_current_user)):
    return user

@app.get('/rank',tags=["rank"],response_model=list[RankItem])
async def get_rank(db: Session = Depends(get_db)):
    ans = await dao.count_grade_times(db)
    rank_list = [RankItem(rank=index+1,username=item[0],count=item[1]) for index,item in enumerate(ans)]
    return rank_list

@app.get('/count',tags=["rank"],response_model=NagativeInfo)
async def count(db: Session = Depends(get_db)):
    return await dao.count_grade(db)

@app.get('/user/count',tags=["rank"],response_model=NagativeInfo)
async def count_by_user(user:UserInDB = Depends(get_current_user),db: Session = Depends(get_db)):
    return await dao.count_grade_by_user(db,user.id)

@app.get('/user/grade',tags=["rank"],response_model=list[int])
async def get_user_grade(user:UserInDB = Depends(get_current_user),db: Session = Depends(get_db)):
    ans = await dao.count_grade_by_user_and_grade(db,user.id)
    grade_list = [0 for i in range(12)]
    for grade,count in ans:
        grade_list[grade] = count
    return grade_list

@app.post('/rank/grade',tags=["rank"],response_model=list[PhotoGrade])
async def get_rank_grade(range:RequestRange,db: Session = Depends(get_db)):
    ans = await dao.count_average_grade(db)
    PhotoList = [PhotoGrade(rank=range.start + index + 1,photo_id=item[0],ave_grade=item[1]) for index, item in enumerate(ans[range.start:range.end])]
    return PhotoList

@app.post('/rank/gradedec',tags=["rank"],response_model=list[PhotoGrade])
async def get_rank_grade_dec(range:RequestRange,db: Session = Depends(get_db)):
    ans = await dao.count_average_grade(db)
    ans = ans[::-1]
    PhotoList = [PhotoGrade(rank=range.start + index + 1,photo_id=item[0],ave_grade=item[1]) for index, item in enumerate(ans[range.start:range.end])]
    return PhotoList

@app.get('/photo/{photo_id}/grade',tags=["rank"],response_model=list[UserGradeRecord])
async def get_photo_grade(photo:Photo = Depends(get_target_photo),db: Session = Depends(get_db)):
    return await dao.get_grade_by_photo_id(db,photo.id)
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
    uvicorn.run('main:app', host="127.0.0.1", port=8000, reload=True, workers=1)