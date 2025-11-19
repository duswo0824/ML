import os
from typing import Dict

from fastapi import FastAPI
from konlpy.tag import Okt
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
import pandas as pd
from joblib import dump, load

from db import get_engine
from logger import Logger

app = FastAPI()
logger = Logger().get_logger(__name__)
app.mount("/view", StaticFiles(directory="view"), name="view")

@app.get("/")
def main():
    return RedirectResponse(url="/view/index.html")

# 토크나이저
def get_tokenizer(text):
   okt = Okt()
   # 명사만 추출해서 리스트 형태로 반환
   return okt.nouns(text)

@app.get("/learn") # 학습
def learn():
    # 1. 데이터 가져오기
    df = pd.read_sql_table('news_score', con=get_engine()) # 쿼리 실행
    logger.info(df.head())

    # 2. x,y 값 구문(배열)
    # 시리즈 형식(각 값에 인덱스) -> 데이터 타입 변경(문자열) -> 배열 변경
    x = df['subject'].astype(str).to_numpy() # x = 기사 제목
    y = df['score'].astype(int).to_numpy() # y = 기사 점수(고용기사가 맞는지)
    logger.info(f'x: {x[:5]}, y: {y[:5]}') # 0~4

    # 3. 모델 정하기 (pipeline)
    # MultinomialNB : 텍스트 분류 기본, 빠른 baseline
    model1 = Pipeline([
        ('vector', CountVectorizer()),
        ('model', MultinomialNB())
    ])

    # LinearSVC(선형 서포트 백터 머신) : 높은 정확도, 안정적 성능
    model2 = Pipeline([
        ('vector', TfidfVectorizer()),
        ('model', LinearSVC())
    ])

    # 4. 학습실행 + 테스트 데이터 분류 + 테스트
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=777, shuffle=True)

    model_list = [] # 모델만 담는다.
    model_dict = {} # 모델명:점수

    for i,model in enumerate([model1, model2]):
        model.fit(x_train, y_train)
        score = model.score(x_test, y_test)
        # 스코어 확인
        logger.info(f'model_{i} : {score}')  # i : 0번 인덱스부터 시작
        # model_list에 model을 넣고
        model_list.append(model)
        model_dict[f'model_{i}'] = score # ← 여기서 누적 저장 O (정답)
        print(f'score: {score}')

        # score_dict에 model_{i+1} : {score} 을 넣는다.
        # model_dict = {f'model_{i}' : score} # 덮어쓰기가된다?

    # 6. 최고 점수 확인 _ 높은 점수를 받은 모델!
    # model_dict에서 최고 값을 가지고 있는 키를 확인
    max_key = max(model_dict, key=model_dict.get) # 대상 딕셔너리, 키를 가져올 딕셔너리
    logger.info(f'max_key: {max_key}:{model_dict[max_key]}')
    idx = int(max_key.split('_')[1]) # [model,0]
    logger.info(f'idx: {idx}')

    # 7. 최고점수 획득한 알고리즘을 저장
    dump(model_list[idx], f'./model/learn.joblib')

    return {'score':model_dict[max_key]}

@app.get("/insert")
def insert():
    file_list = os.listdir('./data')
    # logger.info(f"file_list: {file_list}")

    for item in file_list:
        logger.info(f'{item} 읽어오기')
        df = pd.read_excel('./data/' + item)
        # print(df.head())
        df.dropna(inplace=True)
        # logger.info(f'isNA : {df.isna().sum()}')

        # 날짜 데이터 타입 확인 후 변경
        logger.info(f"날짜 타입 : {df['날짜'].dtype}") # 날짜 타입 : int64(숫자)
        df['날짜'] = df['날짜'].astype(str) # str(문자)
        # 20180909 -> 2018-09-09
        df['날짜'] = pd.to_datetime(df['날짜'],format='%Y%m%d').dt.strftime('%Y-%m-%d')
        # print(df.head())

        # 데이터 프레임의 특정 컬럼들을 row 당 뽑아낸다.
        # apply : 한줄씩 뽑는다.
        # row에 담아서 O아니면 1, 아니면 0 반환한다. 그래서 sum하여 갯수 추출, 계산
        # axis=1, row 방향으로 계산
        df['score']=df[['라벨러1','라벨러2','라벨러3','라벨러4','라벨러5','라벨러6']].apply(
            lambda row: int((row == 'O').sum()/6*100), axis=1 # int : 정수처리
        )

        new_df = df[['날짜','제목','URL','score']]
        new_df.columns = ['reg_date','subject','url','score']
        # print(new_df.head())

        new_df.to_sql('news_score',con=get_engine(),if_exists='append',index=True)
        logger.info('data insert 종료')

    result =  pd.read_sql_query("SELECT COUNT(score)AS cnt FROM news_score",
                             con=get_engine())

    return result.to_dict()

@app.post("/predict") # 예측
def predict(data:Dict[str,str]):
    logger.info(f'data: {data}')
    title = data['news']
    model = load('model/learn.joblib')
    result = model.predict([title])
    logger.info(f'result: {result}')
    return {"result": int(result[0])}
