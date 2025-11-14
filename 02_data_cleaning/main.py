import shutil
from fastapi import FastAPI, UploadFile
import pandas as pd
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()
app.mount('/view', StaticFiles(directory='view'),name='view')

@app.get('/')
def main():
    return RedirectResponse(url='/view/upload.html')

@app.post('/upload')
def upload(file: UploadFile):
    filename = file.filename
    msg = f'{filename} 파일 업로드를 실패 했습니다.'
    try:
        path = 'data/' + filename

        with open(path, 'wb') as temp: # with문으로 파일을 자동으로 닫음
            shutil.copyfileobj(file.file, temp)
        msg = f'{filename} 파일 업로드를 성공 했습니다.'
    except Exception as e:
        print(e)
    return {'msg':msg} # finally: 반드시 실행해야할 cleanup(close같은) 작업이 없어 사용하지 않음

@app.get('/make_df/{filename}') #dataFrame
def make_df(filename: str):
    print(f'read file : {filename}')
    path = f'data/{filename}'
    ext = Path(path).suffix # suffix : 뒤에 있는것(확장자 같은)
    print(f'ext : {ext}')

    df = None

    if ext == '.csv':
        df = pd.read_csv(path)
    if ext == '.json':
        df = pd.read_json(path)
    if ext == '.xlsx':
        df = pd.read_excel(path)
    print(f'df : {df}')

    if df is not None:
        return df.to_json()
    else:
        return None

@app.get('/empty') # 결측치
def empty():
    df = pd.read_csv('data/dirtydata.csv') # 데이터 읽어오기
    # print(df.isna()) # 컬럼별 몇번 row에 결측치가 있는지 확인
    print(df.isna().sum()) # 컬럼별 결측치 갯수
    df.dropna(inplace=True)  # df 에 적용 # df 결측치 삭제
    print(df.isna().sum())
    df.to_csv('data/cleandata.csv', index=False) # csv로 저장
    return{'msg':'결측치 제거 성공'}

@app.get('/wrong/format') # 이상형식
def wrong_format():
    df = pd.read_csv('data/cleandata.csv')
    df['Date'] = pd.to_datetime(df['Date'],format='mixed') # mixed : 주변 데이터 파악해서 수정
    df.to_csv('data/clean_data.csv', index=False)
    return {'msg':'잘못된 형식 변경 성공'}

@app.get('/wrong/data') # 이상치(anomarly)
def wrong_data():
    df = pd.read_csv('data/clean_data.csv')
    for x in df.index:
        # 특정 index의 특정 컬럼만 선택
        # print(df.loc[x]['Duration']) # df.loc[x,'Duration']
        if df.loc[x,'Duration'] > 100:
            df.loc[x,'Duration'] = 60
    df.to_csv('data/clean_data2.csv', index=False)
    return {'msg': '이상치를 보정 하였습니다.'}

@app.get('/duplicate') # 중복데이터
def duplicate_data():
    df = pd.read_csv('data/clean_data2.csv')
    # print(df.duplicated()) # 중복 확인 (True 12,29번)
    # keep=남길 데이터 위치 'first','last',False(다 삭제)
    df.drop_duplicates(inplace=True,keep='last')
    print(df.duplicated())
    df.to_csv('data/clean_data3.csv', index=False)
    return {'msg':'중복데이터를 제거 하였습니다.'}