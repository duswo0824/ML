from fastapi import FastAPI

from database import get_engine
from logger import Logger
import pandas as pd

app = FastAPI()
logger = Logger().get_logger(__name__)

sql = """
SELECT 
	ce.emp_no
	,CONCAT(e.first_name,',',e.last_name) AS name
	,s.salary
	,cde.dept_no
	,(SELECT dept_name FROM departments d WHERE d.dept_no = cde.dept_no) AS team_name
	,e.hire_date
FROM (SELECT emp_no FROM dept_emp_latest_date WHERE to_date = '9999-01-01') ce 
	JOIN employees e on ce.emp_no = e.emp_no
	JOIN current_dept_emp cde on ce.emp_no = cde.emp_no 
	JOIN salaries s on ce.emp_no = s.emp_no 
WHERE s.to_date = '9999-01-01'
"""

emp_df = pd.read_sql(sql, con=get_engine()) # 데이터 프레임 꺼내오기
print(emp_df.head(5)) # df 출력할때는 logger 보다는 print 가 더 보기 좋다.

# dept_no 기준으로 인원수, 급여합계 구하기
@app.get("/group_by/dept")
def group_by_dept():
    # df 을 특정 컬럼으로 그룹화
    # group by 의 기준이 되는 값을 키로 값들을 담게 된다.
    group = emp_df.groupby('team_name')
    logger.info(group.groups)
    # 해당 그룹을 통해 집계함수 실행 # agg(집계)
    result = group.agg(
        count=('dept_no','count'),
        total_sal=('salary','sum')
    )
    print(result) # result 값 터미널에서 확인
    result.to_csv('data/dept.csv') # data 폴더에 생성
    return result.to_dict()

@app.get("/group_by/team/mean")
def group_by_mean():
    # 팀별 급여 평균 추출
    group = emp_df.groupby('team_name')
    
    result = group.agg(
        mean_sal=('salary','mean')
    )
    return result.to_dict()

@app.get("/group_by/team_year/mean")
def team_year_mean():

    sql = """
    SELECT 
	    ce.emp_no
	    ,(SELECT dept_name FROM departments d WHERE d.dept_no = cde.dept_no) AS team_name
	    ,CONCAT(e.first_name,',',e.last_name) AS name
	    ,YEAR(s.from_date) AS from_year 
	    ,s.salary
    FROM (select emp_no FROM dept_emp_latest_date WHERE to_date = '9999-01-01') ce 
	    JOIN employees e ON ce.emp_no = e.emp_no
	    JOIN current_dept_emp cde ON ce.emp_no = cde.emp_no 
	    JOIN salaries s ON ce.emp_no = s.emp_no;
    """
    df = pd.read_sql(sql, con=get_engine())
    # 팀별,연도별 급여 평균
    group = df.groupby(['team_name','from_year'])
    result = group.agg(mean=('salary','mean'))
    print(result)
    result.to_csv('data/team_year_mean.csv')
    return result.to_json()

# 피벗을 활용하여 테이블을 복기 좋게 변경해주자
@app.get("/pivot")
def pivot():
    df = pd.read_csv('data/team_year_mean.csv')
    pivot_df = df.pivot_table(
        columns='from_year', # 컬럼의 기준
        index='team_name', # 인덱스 기준(row)
        values='mean',
        fill_value=0, # 피봇중에 공백값이 생길경우 채워질값
        margins=True, # 총 합계 행/열 추가 여부
        margins_name='salary_mean' # margins=True 일 경우 이름(안주면 All로 표시)
    )
    pivot_df.to_csv('data/pivot.csv')
    return {'mag':'pivot OK!'}
