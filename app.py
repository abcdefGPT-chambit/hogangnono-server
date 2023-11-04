from flask import Flask, jsonify, request
import pandas as pd
from models import db, AptReview, AptTrade
from config import config

app = Flask(__name__)

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


if __name__ == '__main__':
    app.run()
