from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from db_models import db, AptReview, AptTrade, AptInfo
from config import config

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

if __name__ == '__main__':
    app.run()
