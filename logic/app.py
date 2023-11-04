from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import AptInfo
from models import AptReview
from models import AptTrade
from config import config

app = Flask(__name__)

# 데이터베이스 연결 설정
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 이 옵션을 False로 설정하여 추가 메모리를 사용하지 않도록 합니다.

db = SQLAlchemy(app)

def insertdata(apt_code, apt_name):
    if not apt_code or not apt_name:
        return "apt_code 혹은 apt_name이 정상적으로 주어지지 않았습니다.", 400

    new_entry = AptInfo(apt_code=apt_code, apt_name=apt_name)
    db.session.add(new_entry)
    try:
        db.session.commit()
        return "데이터 저장 완료"
    except Exception as e:
        db.session.rollback()
        return str(e), 500

@app.route('/insertdata')
def web_insertdata():
    insertdata()
    return "Data inserted successfully!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 이제 모델에 기반하여 테이블을 생성합니다.
    app.run()

# .csv 파일의 데이터를 읽어서 db에 저장하기
# apt_code와 apt_name을 넘겨주면 해당하는 데이터 넘겨주기