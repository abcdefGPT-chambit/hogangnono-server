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
from sqlalchemy import case, func

from langchain.agents import create_pandas_dataframe_agent
# GPT API 설정
import constants

os.environ["OPENAI_API_KEY"] = constants.APIKEY
chat = ChatOpenAI(model_name='gpt-4', temperature=0, openai_api_key=constants.APIKEY)
# temperature 값을 수정하여 모델의 온도를 변경할 수  있다. default는 0.7, 1에 가까울 수록 다양성 증진
# chat([SystemMessage(content="완결된 한국어 문장으로 대답해줘")])

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
agent1 = create_pandas_dataframe_agent(chat, Seoul_df, verbose=True)
agent2 = create_pandas_dataframe_agent(chat, Data_df, verbose=True)
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


def getFile(filename):
    review_df = pd.read_csv(filename)
    for index, row in review_df.iterrows():
        review = AptReview(
            apt_code=row['apt_code'],
            category=row['category'],
            review=row['review']
        )
        db.session.add(review)


# CSV 파일의 데이터를 DB에 구축
@app.route('/insertdata', methods=['POST'])
def web_insertdata():
    getFile('database/dataset/apt_review/1_Gracium_Label.csv')
    getFile('database/dataset/apt_review/2_Heliocity_Label.csv')
    getFile('database/dataset/apt_review/3_Mapo_raemian_pruzio_Label.csv')
    getFile('database/dataset/apt_review/4_Banpo_raemian_firstage_Label.csv')
    getFile('database/dataset/apt_review/5_Dogok_rexle_Label.csv')
    getFile('database/dataset/apt_review/6_recents_Label.csv')
    getFile('database/dataset/apt_review/7_DMC_parkview_xi_Label.csv')
    getFile('database/dataset/apt_review/8_Gileum_raemiman_centerpiece_Label.csv')
    getFile('database/dataset/apt_review/9_arteon_Label.csv')
    getFile('database/dataset/apt_review/10_parkrio_Label.csv')

    trade_df = pd.read_csv('database/dataset/apt_trade/Apt_transaction_result.csv')
    for index, row in trade_df.iterrows():
        trade = AptTrade(
            apt_code=row['apt_code'],
            apt_sq=row['apt_sq'],
            avg_price=row['avg_price'],
            top_avg_price=row['top_avg_price'],
            bottom_avg_price=row['bottom_avg_price'],
            recent_avg=row['recent_avg'],
            recent_top=row['recent_top'],
            recent_bottom=row['recent_bottom'],
            trade_trend=row['trade_trend'],
            price_trend=row['price_trend']
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
        {'apt_sq': trade.apt_sq, 'avg_price': trade.avg_price, 'top_avg_price': trade.top_avg_price,
         'bottom_avg_price': trade.bottom_avg_price, 'recent_avg': trade.recent_avg, 'recent_top': trade.recent_top,
         'recent_bottom': trade.recent_bottom, 'trade_trend': trade.trade_trend, 'price_trend': trade.price_trend}
        for trade in trades
    ]

    # JSON으로 결과 반환
    return jsonify({
        'apt_code': apt_code,
        'apt_name': apt_name,
        'reviews': review_list,
        'trades': trade_list
    })


# 모든 아파트의 이름과 평형을 반환하는 API
@app.route('/get/all-name-sq', methods=['GET'])
def web_get_name_sq():
    # AptInfo와 AptTrade를 조s인하여 필요한 데이터를 가져옴
    results = db.session.query(AptInfo.apt_name, AptTrade.apt_sq) \
        .join(AptTrade, AptInfo.apt_code == AptTrade.apt_code) \
        .all()

    # 결과 데이터를 JSON 형식으로 변환
    name_sq_list = [
        {
            "apt_name": result.apt_name,
            "apt_sq": f"{result.apt_sq}㎡"
        }
        for result in results
    ]

    # JSON으로 결과 반환
    return jsonify({"name_and_sq": name_sq_list})

# 모든 아파트의 이름을 반환하는 API
@app.route('/get/all-name', methods=['GET'])
def web_get_name():

    results = db.session.query(AptInfo.apt_name).all()

    # 결과 데이터를 JSON 형식으로 변환
    name_sq_list = [
        {
            "apt_name": result.apt_name,
        }
        for result in results
    ]

    # JSON으로 결과 반환
    return jsonify(name_sq_list)

@app.route('/get_answers', methods=['POST'])
def get_answers():
    data = request.json
    if not data:
        return jsonify({'error': 'No string provided'}), 400

    provided_string = data['message']
    provided_string = chat([HumanMessage(content=provided_string + "영어로 번역해줘")]).content
    answer = agent2.run(provided_string)
    # answer = agent2.run(provided_string + "Please add a basis for the answer")
    answer = chat([HumanMessage(content=answer + "완결된 한국어 문장으로 번역해줘")]).content

    # 답변을 JSON 형식으로 구성
    qna_pairs = [
        {"answer": answer}
    ]

    # JSON으로 변환하여 반환
    return jsonify(qna_pairs)


def search_apartments(search_str):
    if len(search_str) == 1:
        results = AptInfo.query.filter(AptInfo.apt_name.like(f"%{search_str}%")).all()
        apartments = [
            {"apt_code": apt.apt_code, "apt_name": apt.apt_name}
            for apt in results
        ]
        return apartments
    else:
        case_statements = [case(*[(AptInfo.apt_name.like(f'%{char}%'), 1)], else_=0) for char in search_str]

        # 총 점수 계산
        score_column = func.coalesce(sum(case_statements), 0).label('score')

        # 쿼리 생성 및 실행
        query = AptInfo.query.with_entities(AptInfo, score_column).filter(score_column > 0).order_by(
            score_column.desc())
        results = query.all()

        apartments = [
            {"apt_code": apt[0].apt_code, "apt_name": apt[0].apt_name}
            for apt in results
        ]
        return apartments


@app.route('/search', methods=['POST'])
def search_apt():
    data = request.json
    if not data:
        return jsonify({'error': 'No string provided'}), 400

    provided_string = data['message']

    apartment_list = search_apartments(provided_string)

    # JSON으로 변환하여 반환
    return jsonify(apartment_list)


# 로드밸런서의 테스트를 위한 기본 응답
@app.route('/', methods=['GET'])
def initial_request():
    return jsonify({'success': 'initial request'}), 200


if __name__ == '__main__':
    app.run()
