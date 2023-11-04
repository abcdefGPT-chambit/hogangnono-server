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