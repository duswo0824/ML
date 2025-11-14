import shutil

import pandas as pd
from fastapi import FastAPI, UploadFile
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

from database import get_engine
from logger import Logger

app = FastAPI()
logger = Logger().get_logger(__name__)

app.mount("/view", StaticFiles(directory="view"), name="view")

@app.get("/")
def main():
    return RedirectResponse('/view/upload.html')

@app.post("/upload")
def upload(file: UploadFile):
    logger.info(f"upload file: {file.filename}")
    msg = f'{file.filename} upload 실패'

    try:

        with open(f'data/{file.filename}','wb') as temp: # 파일 읽어오기
            shutil.copyfileobj(file.file, temp)
        msg = f'{file.filename} upload 성공'
    except Exception as e:
        logger.error(e)
    return {'msg':msg}

# csv 를 불러와서 결측치를 제거하고 health 라는 테이블 명으로 저장하기
@app.get("/create_table")
def create_table():
    
    df = pd.read_csv('data/import.csv')
    print(df.isna().sum()) # NA 확인
    df.dropna(inplace=True) # NA 삭제 # True : df 자체에 적용
    
    # name = 테이블명
    # con = 사용하는 DB 엔진
    # if_exists = [테이블이 이미 존재하면?] 'replace'(덮어쓰기),'append'(그냥추가),'fail'(에러)
    # index = index 값 DB에 넣을지 여부
    # schema = database 이름(설정하지 않을 경우 database.py의 값을 따름_기본으로따라감)
    df.to_sql('health', con=get_engine(), if_exists='replace', index=False)
    
    return {'msg':'import.csv 테이블 저장 완료'}

# 테이블에 있는 모든 데이터를 DataFrame 으로 만들기
@app.get("/get_table/{table}")
def get_table(table: str):
    logger.info(f"get table: {table}")
    # table_name=테이블명, con=엔진, schema=DB
    df = pd.read_sql_table(table_name=table, con= get_engine())
    print(df.head(5))
    return df.to_dict() # json이 안정적(바꿔가면서 해보기)

# 쿼리문을 이용해 DataFrame 만들기
@app.get("/read_sql")
def read_sql():
    sql = "SELECT * FROM health WHERE Calories > 300 ORDER BY Calories DESC"
    # sql=sql구문, con=엔진, schema=DB
    df = pd.read_sql_query(sql=sql, con=get_engine())
    print(df.head(5))
    return df.to_dict()
