from sqlalchemy import create_engine

id = 'web_user'
password = 'pass'
host = 'localhost'
port = 3306
db = 'mydb'
url = f'mysql+pymysql://{id}:{password}@{host}:{port}/{db}'

engine = create_engine(url, echo=True, pool_size=1)

def get_engine():
    return engine
