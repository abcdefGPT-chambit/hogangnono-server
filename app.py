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



if __name__ == '__main__':
    app.run()
