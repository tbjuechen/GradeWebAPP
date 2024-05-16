import os

# PHOTOPATH = os.path.join(os.path.expanduser('~'),'Downloads','beauty')
PHOTOPATH = 'F:\\Scripts\\xhsSpider\\result_2\\female'

from schema import PhotoCreate
from dao import create_photo
from dependencies import get_db


async def add_photo():
    db = next(get_db())
    # 遍历文件夹中的所有文件
    for root, dirs, files in os.walk(PHOTOPATH):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            # 创建照片
            photo = PhotoCreate(name=file_name, location=file_path)
            try:
                await create_photo(db, photo)
            except Exception as e:
                print(e)
