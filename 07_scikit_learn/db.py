from sqlalchemy import create_engine

id = 'web_user'
pw = 'pass'
host = 'localhost'
port = 3306
db = 'mydb'
url = f'mysql+pymysql://{id}:{pw}@{host}:{port}/{db}'

engine = create_engine(url, pool_size=1)

def get_engine():
    return engine
