from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from db_models import db, AptReview, AptTrade, AptInfo
from config import config
import os
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from langchain.agents import create_pandas_dataframe_agent

# GPT API 설정
import constants
os.environ["OPENAI_API_KEY"] = constants.APIKEY
chat = ChatOpenAI(model_name='gpt-4', temperature=0, openai_api_key=constants.APIKEY)
#temperature 값을 수정하여 모델의 온도를 변경할 수  있다. default는 0.7, 1에 가까울 수록 다양성 증진
#chat([SystemMessage(content="완결된 한국어 문장으로 대답해줘")])

# Load Data
df = pd.read_csv('data/Seoul_Transaction_Sep.csv')
# print(df.head())
Seoul_df = df.copy()
Data_df = df.copy()
Data_df.drop(0, inplace=True)
Data_df.reset_index(drop=True, inplace=True)
Seoul_df = Seoul_df.iloc[:1]

# GPT version 3 사용
# agent1 = create_pandas_dataframe_agent(OpenAI(temperature=0),Seoul_df,verbose=True)
# agent2 = create_pandas_dataframe_agent(OpenAI(temperature=0),Data_df,verbose=True)
# GPT version 4 사용
agent1 = create_pandas_dataframe_agent(chat,Seoul_df,verbose=True)
agent2 = create_pandas_dataframe_agent(chat,Data_df,verbose=True)
# verbose는 생각의 과정을 설정해준다.


app = Flask(__name__)

# 모든 도메인에 대해 CORS를 허용하도록 설정
CORS(app)

# DB 설정
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()

# CSV 파일의 데이터를 DB에 구축
@app.route('/insertdata', methods=['POST'])
def web_insertdata():

    review_df = pd.read_csv('dataset/20231105_apt_review.csv')
    for index, row in review_df.iterrows():
        review = AptReview(
            apt_code=row['apt_code'],
            category=row['category'],
            review=row['review']
        )
        db.session.add(review)

    trade_df = pd.read_csv('dataset/20231105_apt_trade.csv')
    for index, row in trade_df.iterrows():
        trade = AptTrade(
            apt_code=row['apt_code'],
            highest=row['highest'],
            lowest=row['lowest'],
            high_floor=row['high_floor'],
            middle_floor=row['middle_floor'],
            low_floor=row['low_floor'],
            trade_trend=row['trade_trend']
        )
        db.session.add(trade)

    db.session.commit()

    return "{'status' : '200', 'message' : 'ok'}"

# 프론트 측으로부터 받은 apt_code와 apt_name을 바탕으로 데이터들 반환
@app.route('/getdata', methods=['GET'])
def web_getdata():
    apt_code = request.args.get('apt_code')
    apt_name = request.args.get('apt_name')

    if not apt_code or not apt_name:
        return jsonify({'error': 'Please provide both apt_code and apt_name'}), 400

    # apt_review 데이터
    reviews = AptReview.query.filter_by(apt_code=apt_code).all()
    review_list = [
        {'category': review.category, 'review': review.review}
        for review in reviews
    ]

    # apt_trade 데이터
    trades = AptTrade.query.filter_by(apt_code=apt_code).all()
    trade_list = [
        {'highest': trade.highest, 'lowest': trade.lowest, 'high_floor': trade.high_floor,
         'middle_floor': trade.middle_floor, 'low_floor': trade.low_floor, 'trade_trend': trade.trade_trend}
        for trade in trades
    ]

    # JSON으로 결과 반환
    return jsonify({
        'apt_code': apt_code,
        'apt_name': apt_name,
        'reviews': review_list,
        'trades': trade_list
    })

@app.route('/gpt_api', methods=['POST'])
def gpt_api():
    data = request.json
    if not data:
        return jsonify({'error': 'No string provided'}), 400

    provided_string = data['message']

    response = return_from_gpt(provided_string)
    response_dict = {'content': response.content, 'type': response.type}
    return jsonify({'message': response_dict})

def return_from_gpt(message):
    response = chat([SystemMessage(content="한국어로 완성된 문장으로 대답해줘"), HumanMessage(content=message)])
    return response


@app.route('/get_answers', methods=['POST'])
def get_answers():
    data = request.json
    if not data:
        return jsonify({'error': 'No string provided'}), 400

    provided_string = data['message']
    answer = agent2.run( provided_string + "완결된 한국어 문장으로 대답해줘. 변수를 출력하는게 아닌 실제 값을 알려줘")

    # 질문과 답변을 쌍으로 묶어 JSON 형식으로 구성
    qna_pairs = [
        {"question": provided_string, "answer": answer}
    ]

    # JSON으로 변환하여 반환
    return jsonify(qna_pairs)


# 로드밸런서의 테스트를 위한 기본 응답
@app.route('/', methods=['GET'])
def initial_request():
    return jsonify({'success': 'initial request'}), 200

if __name__ == '__main__':
    app.run()
