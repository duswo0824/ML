import shutil

import matplotlib.pyplot as plt
import pandas as pd
from fastapi import FastAPI, UploadFile
from starlette.responses import RedirectResponse, HTMLResponse
from starlette.staticfiles import StaticFiles
from wordcloud import WordCloud

from database import get_engine

app = FastAPI()

app.mount("/view", StaticFiles(directory="view"), name="view")
app.mount("/data", StaticFiles(directory="data"), name="data")

@app.get("/")
def main():
    return RedirectResponse('/view/upload.html')

@app.post("/upload")
def upload(file: UploadFile):
    # 1. upload 페이지에서 맛집.csv를 업로드
    path = f'data/{file.filename}'
    with open(path,'wb') as temp: # 파일 읽어오기 # with:open 할때 사용하면 자동으로 닫음
        shutil.copyfileobj(file.file, temp)

    # 2. 받은 내용을 DataFrame화 시킴(한글깨짐 해결)
    df = pd.read_csv(path, encoding='utf-8')
    # print(df.head(5)) # 터미널
    print(df['메뉴'].head(10))

    # 3. DB에 저장 ['메뉴']만 저장
    df['메뉴'].to_sql('favor_menu', con=get_engine(), if_exists='replace', index=False)
    return {'msg': 'upload 성공'}  # console

# WorldCloud 만들기
# pip install wordcloud
# pip install konlpy # 한국어 형태소 분석기(명사 위주로)
@app.get("/make_wc")
def make_wc():
    # 1. DB에서 데이터 호출
    df = pd.read_sql_table('favor_menu', con=get_engine())
    # 2. 문자열로 만든다.
    text = df.to_string(index=False, header=False)
    # 공백 삭제, (콤마,) 대신 줄바꿈
    text = text.replace(' ', '').replace(',', '\n')
    # print(text)
    # 3. 워드클라우드로 변환
    wc = WordCloud(
        font_path='C:\\Windows\\Fonts\\H2GTRE.TTF',
        width=800,
        height=800,
        background_color='white',
    ).generate_from_text(text)

    plt.imshow(wc) # 이미지화
    plt.axis('off') # 축 눈금 삭제
    plt.savefig('data/wordcloud.png',transparent=True)
    return HTMLResponse(content='<img src="data/wordcloud.png"/>')
