import mpld3
from fastapi import FastAPI
from starlette.responses import RedirectResponse, HTMLResponse
from starlette.staticfiles import StaticFiles
import pandas as pd
from matplotlib import pyplot as plt

from database import get_engine
from logger import Logger

app = FastAPI()
logger = Logger().get_logger(__name__)

app.mount("/view", StaticFiles(directory="view"), name="view")
app.mount("/fig", StaticFiles(directory="fig"), name="fig")

@app.get("/")
def main():
    return RedirectResponse(url="/view/index.html")

@app.get("/showFig")
def show_fig(type: str):
    logger.info(f'type: {type}')

    # 1. SQL로 데이터 가져오기(사원번호 1000 의 연도별 급여 변화)
    sql = '''
    SELECT 
	    year(from_date)AS year
	    ,salary 
    FROM salaries WHERE emp_no = 10001 ORDER BY year;
    '''
    df = pd.read_sql_query(sql, con=get_engine())
    # print(df)

    # 2. plot으로 차트 그리기
    graph = plt.figure()  # 그래프 창을 저장
    
    set_font(plt) # 한글깨짐 방지
    
    plt.plot(df['year'], df['salary'], 'r-')
    plt.title('10001 사원의 연간 급여 변화')
    plt.xlabel('연도')
    plt.ylabel('급여')
    # plt.plot(x,y,style)
    # 3. 그린 차트 저장하기(이미지/HTML)
    fig = '' # 선언
    if type == 'image':
        path = 'fig/salaries.png'
        graph.savefig(path, transparent=True)  # 그래프를 특정 경로에 저장(배경은 투명하게)
        fig = f'<img src="/{path}"/>'
    else: # html
        fig = mpld3.fig_to_html(graph)
    # 4. 반환
    return HTMLResponse(content=fig)

@app.get("/sub_plot")
def sub_plot(type: str):
    graph = plt.figure()
    fig = ''

    import numpy as np
    x = np.linspace(-2,2,30)

    plt.subplot(2,2,1)
    plt.plot(x,x)
    plt.subplot(2, 2, 2)
    plt.plot(x, x**2)
    plt.subplot(2, 2, 3)
    plt.plot(x, x**3)
    plt.subplot(2, 2, 4)
    plt.plot(x, x**4)
    plt.subplots_adjust(wspace=0.2, hspace=0.3)

    # plt.show() 여기선 사용 X
    if type == 'image':
        path = 'fig/subplot.png'
        graph.savefig(path, transparent=True)
        fig = f'<img src="/{path}"/>'
    else: # html
        fig = mpld3.fig_to_html(graph)

    return HTMLResponse(content=fig)

def set_font(plt):
    font_pth = 'C:/Windows/Fonts/malgun.ttf'
    # 해당 경로의 폰트파일을 이용해 폰트 속성 추출
    import matplotlib.font_manager as fm
    font_props = fm.FontProperties(fname=font_pth)
    # 전체 폰트 설정
    plt.rcParams['font.family'] = font_props.get_name()
    # 음수 부호 깨짐 방지
    plt.rcParams['axes.unicode_minus'] = False
