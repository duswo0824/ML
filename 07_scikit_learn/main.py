from typing import Dict

from fastapi import FastAPI
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction import text
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from starlette.responses import RedirectResponse
import pandas as pd
from starlette.staticfiles import StaticFiles
from joblib import dump, load

from db import get_engine
from logger import Logger

app = FastAPI()
logger = Logger().get_logger(__name__)

app.mount("/view", StaticFiles(directory="view"), name="view")

@app.get("/")
def main():
    return RedirectResponse(url="/view/index.html")

@app.get("/insert")
def insert():
    news = fetch_20newsgroups(subset='all')
    print(news.keys()) # dict_keys(['data', 'filenames', 'target_names', 'target', 'DESCR'])
    # news.data - 학습데이터
    # news.target - 문제에 대한 답(숫자)
    # news.target_names - 해당 숫자에 대한 문자열(이름)
    
    # 1. news_groups에 data와 target 추가
    logger.info('dataFrame 생성!')
    df = pd.DataFrame({'content' : news['data'], 'target' : news['target']})
    print(df.head(5))
    # DB 저장
    df.to_sql('news_groups', con=get_engine(), if_exists='append', index=False)
    # 테이블이 미리 생성 content=longtext 유지 하려면, if_exists='append'(추가)
    logger.info('dataFrame DB 입력 종료!')

    logger.info('dataFrame 생성2!')
    # 2. target_names을 news_groups_target_name 이라는 테이블에 추가
    df = pd.DataFrame({'target_name': news['target_names']})
    df.to_sql('news_groups_target_name', con=get_engine(), if_exists='replace')
    # index=False - 인덱스를 받지 않겠다는 의미
    logger.info('dataFrame DB 입력 종료2!')
    return {"msg": "insert OK"}

# 학습
@app.get("/learn")
def learn():
    # 1. 데이터 가져오기
    sql = """
    SELECT ng.content, tn.target_name	
	    FROM news_groups ng JOIN news_groups_target_name tn ON ng.target = tn.index;
    """

    df = pd.read_sql(sql, con=get_engine())
    print(df.head(5))
    # x = 문제 배열, y = 정답 배열
    # 시리즈 형식(각 값에 인덱스) -> 데이터 타입 변경(문자열) -> 배열 변경
    x = df['content'].astype(str).to_numpy()
    y = df['target_name'].astype(str).to_numpy()
    # logger.info(x[0:9])
    # logger.info(y[:10]) # 0~9

    # 2. 데이터 분리
    # train : 학습용, test : 시험용
    x_train, x_test, y_train, y_test = train_test_split(x,y, test_size=0.3, random_state=7, shuffle=True)

    # 3. 학습(멀티노미얼 방식이 어떻게 학습했는지 확인)

    model = Pipeline([ # set : 변경할수 없는 리스트
        ('vector',TfidfVectorizer(stop_words='english')), # 스케일(데이터 정제) - 단어 출현 빈도수를 수치화
        ('model',MultinomialNB())
    ])
    model.fit(x_train, y_train)

    # 4. 스코어 확인
    score = model.score(x_test, y_test)

    # 5. 0.8 이상이면 학습된 알고리즘 저장(model/learn.joblib)
    if score >= 0.8:
        dump(model,"model/learn.joblib")

    # 6. 점수를 {"score":87} 형태로 클라이언트에게 전달
    return{"score":int(score*100)} # score : 87

# 예측
@app.post("/predict")
def predict(data:Dict[str,str]):
    logger.info(f'data: {data}')
    # 내용을 추출
    post = data['news']
    # 학습 알고리즘 load
    model = load('model/learn.joblib')
    # 예측 실행
    result = model.predict([post])
    logger.info(f'result: {result}')
    # 결과 반환
    return {"result":result[0]}