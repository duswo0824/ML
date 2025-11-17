from sqlalchemy import create_engine

id = 'web_user'
password = 'pass'
host = 'localhost:3306'
db = 'employees'
url = f'mysql+pymysql://{id}:{password}@{host}/{db}'

engine = create_engine(url, echo=True, pool_size=1)

def get_engine():
    return engine
