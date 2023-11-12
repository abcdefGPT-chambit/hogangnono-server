from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class AptInfo(db.Model):
    __tablename__ = 'apt_info'
    apt_code = db.Column(db.String(255), primary_key=True)
    apt_name = db.Column(db.String(255))

class AptReview(db.Model):
    __tablename__ = 'apt_review'
    id = db.Column(db.Integer, primary_key=True)  # 각 리뷰의 고유 ID
    apt_code = db.Column(db.String(255), db.ForeignKey('apt_info.apt_code'))  # 외래 키로 설정
    category = db.Column(db.BigInteger)
    review = db.Column(db.String(255))

class AptTrade(db.Model):
    __tablename__ = 'apt_trade'
    id = db.Column(db.Integer, primary_key=True)  # 각 거래의 고유 ID
    apt_code = db.Column(db.String(255), db.ForeignKey('apt_info.apt_code'))  # 외래 키로 설정
    apt_sq = db.Column(db.Integer)
    avg_price = db.Column(db.String(255))
    top_avg_price = db.Column(db.String(255))
    bottom_avg_price = db.Column(db.String(255))
    recent_avg = db.Column(db.String(255))
    recent_top = db.Column(db.String(255))
    recent_bottom = db.Column(db.String(255))
    trade_trend = db.Column(db.String(255))
    price_trend = db.Column(db.String(255))
