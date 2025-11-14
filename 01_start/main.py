from fastapi import FastAPI
import pandas as pd

app = FastAPI()

@app.get('/')
def main():
    mydata = {
        'cars':['BMW','Volvo','Ford'],
        'passings':[3,7,2]
    }

    df = pd.DataFrame(mydata)
    print(df)
    # 순수 DataFrame 형태로는 반환할 수 없다.
    # 그래서 JSON 과 비슷한 형태로 변환해서 보내야 한다.
    # return df.to_json() # json 형태의 문자열로 전송(다른 언어와 통신시 이게 더 안정적)
    return df.to_dict() #dictionary 형태로 전송

