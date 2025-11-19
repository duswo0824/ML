# 백업용
import os

from fastapi import FastAPI
from konlpy.tag import Okt
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.neural_network import MLPClassifier
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
import pandas as pd

from db import get_engine
from logger import Logger

app = FastAPI()
logger = Logger().get_logger(__name__)
app.mount("/view", StaticFiles(directory="view"), name="view")

@app.get("/")
def main():
    return RedirectResponse(url="/view/index.html")

# 토크나이저 (형태소 분석기)
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
        ('vector', CountVectorizer(tokenizer=get_tokenizer)),
        ('model', MultinomialNB())
    ])

    # LinearSVC(선형 서포트 백터 머신) : 높은 정확도, 안정적 성능
    model2 = Pipeline([
        ('vector', TfidfVectorizer(tokenizer=get_tokenizer)),
        ('model', LinearSVC())
    ])

    import sklearn.ensemble as en
    # GradientBoostingClassifier : 높은 성능,과적합 제어,자동 특징 선택
    model3 = Pipeline([
        ('vector', TfidfVectorizer(tokenizer=get_tokenizer)),
        ('model', en.GradientBoostingClassifier(
            learning_rate=0.1, max_depth=3, n_estimators=200))
    ])

    # MLPClassifier(딥러닝 기반 뉴럴 네트워크) : 복잡한 패턴 학습 가능, 딥러닝 경험용
    model4 = Pipeline([
        ('vector', TfidfVectorizer()),
        ('model', MLPClassifier(
            max_iter=1000,hidden_layer_sizes=(30,30,30),random_state=42)),
    ])

    # 4. 학습실행 + 테스트 데이터 분류 + 테스트
    import sklearn.model_selection as ms

    for i,model in enumerate([model1, model2]):
        model.fit(x, y)
        score = ms.cross_val_score(model, x, y, cv=5)

        # 6. 최고 점수 확인
        logger.info(f'model_{i} : {score.mean()}')

    # 7. 최고점수 획득한 알고리즘을 저장
    return {'msg':'learn 종료!'}

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
