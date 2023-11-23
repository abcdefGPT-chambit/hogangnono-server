from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import pandas as pd
from db_models import db, AptReview, AptTrade, AptInfo
from config import config
import os
import openai
from sqlalchemy import case, func

# GPT API 설정
import constants

# Load Data
df = pd.read_csv('data/Seoul_Transaction_Sep.csv')
# print(df.head())
Seoul_df = df.copy()
Data_df = df.copy()
Data_df.drop(0, inplace=True)
Data_df.reset_index(drop=True, inplace=True)
Seoul_df = Seoul_df.iloc[:1]


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
@cross_origin()
def get_answers():
    data = request.json
    if not data:
        return jsonify({'error': 'No string provided'}), 400

    provided_string = data['message']
    openai.api_key = constants.APIKEY

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system",
             "content": "You're a real estate expert who explains apartment transactions. give me answer with korean"},
            {"role": "user", "content": "I'd like to ask about the last year's transaction data I have"},
            {"role": "assistant",
             "content": "Absolutely, I'd be happy to help! Please share the transaction data you have and specify what exactly would you like to know or understand from it."},
            {"role": "user",
             "content": "구분,2022년 9월,10월,11월,12월,2023년 1월,2월,3월,4월,5월,6월,7월,8월,9월,서울특별시,607,559,727,835,1411,2450,2985,3186,3427,3845,3583,3852,3360, 강남구,31,30,36,40,95,184,181,189,262,252,239,266,194,강동구,19,32,39,46,122,200,178,247,213,229,206,220,180,강북구,12,11,8,45,24,37,77,50,56,126,64,186,49,강서구,30,27,42,50,52,147,146,160,175,206,149,187,190,관악구,17,15,14,14,29,57,62,79,191,96,99,112,108,광진구,11,9,7,57,34,45,48,60,70,64,65,78,78,구로구,41,40,24,26,45,89,129,156,134,134,146,156,144,금천구,14,9,146,13,13,33,52,55,39,57,63,56,54,노원구,30,43,45,57,133,190,188,216,232,272,281,304,257,도봉구,27,17,28,20,67,104,93,86,92,109,118,111,101,동대문구,24,25,31,28,83,106,119,144,155,177,151,139,127,동작구,21,20,15,24,39,66,106,108,120,132,146,138,123,마포구,20,19,19,33,54,92,126,136,166,166,179,167,140,서대문구,14,22,18,26,47,93,106,117,119,128,153,156,142,서초구,20,17,28,29,46,82,120,151,139,181,187,194,141,성동구,14,18,9,25,41,87,112,132,153,170,200,170,168,성북구,33,40,36,50,97,144,152,168,177,181,177,198,178,송파구,29,45,51,86,148,254,230,279,294,288,265,265,256,양천구,31,16,19,28,56,114,110,149,137,173,161,186,175,영등포구,69,29,35,66,55,103,126,159,187,287,169,185,177,용산구,12,8,14,10,13,23,40,43,44,66,50,57,61,은평구,34,27,31,29,54,95,370,145,124,121,143,156,122,종로구,14,4,8,6,7,19,22,17,30,30,22,37,43,중구,11,14,7,11,16,31,30,45,51,53,62,58,52,중랑구,29,22,17,16,41,55,62,95,67,147,88,70,100"},
            {"role": "assistant",
             "content": "Sure, I see that you've shared transaction data (presumably apartments sold?) for various districts in Seoul over the period from September 2022 to September 2023. Is there a specific question or type of analysis you are looking for with this data?"},
            {"role": "user", "content": provided_string}
        ]
    )

    # 답변을 JSON 형식으로 구성
    qna_pairs = [
        {"answer": response.choices[0].message.content}
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


# @app.route('/gpt_api', methods=['POST'])
# @cross_origin()
# def gpt_api():
#     data = request.json
#     if not data:
#         return jsonify({'error': 'No string provided'}), 400
#
#
#     # response = return_from_gpt(provided_string)
#     # response_dict = {'content': response.content, 'type': response.type}
#     return jsonify({'message': response_dict})


# 로드밸런서의 테스트를 위한 기본 응답
@app.route('/', methods=['GET'])
def initial_request():
    return jsonify({'success': 'initial request'}), 200


if __name__ == '__main__':
    app.run()