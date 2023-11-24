# 실행방법: uvicorn fast_api:app --reload
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from db_models import db, AptReview, AptTrade, AptInfo
from config import config
import openai
from sqlalchemy import case, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# GPT API 설정
import constants

# Load Data
df = pd.read_csv('data/Seoul_Transaction_Sep.csv')
Seoul_df = df.copy()
Data_df = df.copy()
Data_df.drop(0, inplace=True)
Data_df.reset_index(drop=True, inplace=True)
Seoul_df = Seoul_df.iloc[:1]

app = FastAPI()

# Enable CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 오리진 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드 허용
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)

# DB 설정 (비동기 데이터베이스 엔진)
DATABASE_URL = config.SQLALCHEMY_DATABASE_URI
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# csv 파일 정보 DB 삽입 API에서 apt_review
async def insert_apt_reviews(session: AsyncSession, filename: str):
    review_df = pd.read_csv(filename)
    for index, row in review_df.iterrows():
        review = AptReview(
            apt_code=row['apt_code'],
            category=row['category'],
            review=row['review']
        )
        session.add(review)
    await session.commit()

# csv 파일 정보 DB 삽입 API에서 apt_trade
async def insert_apt_trades(session: AsyncSession):
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
        session.add(trade)
    await session.commit()

# csv 파일 정보 DB 삽입 API(apt_review, apt_trade)
@app.post("/insertdata")
async def web_insertdata():
    async with AsyncSessionLocal() as session:
        # Insert AptReviews
        review_files = [
            'database/dataset/apt_review/1_Gracium_Label.csv',
            'database/dataset/apt_review/2_Heliocity_Label.csv',
            'database/dataset/apt_review/4_Banpo_raemian_firstage_Label.csv',
            'database/dataset/apt_review/5_Dogok_rexle_Label.csv',
            'database/dataset/apt_review/6_recents_Label.csv',
            'database/dataset/apt_review/7_DMC_parkview_xi_Label.csv',
            'database/dataset/apt_review/8_Gileum_raemiman_centerpiece_Label.csv',
            'database/dataset/apt_review/9_arteon_Label.csv',
            'database/dataset/apt_review/10_parkrio_Label.csv'
        ]
        for file in review_files:
            await insert_apt_reviews(session, file)

        # Insert AptTrades
        await insert_apt_trades(session)

        return {"status": 200, "message": "Data insertion successful"}

@app.get("/getdata")
async def web_getdata(apt_code: str, apt_name: str):
    # 데이터 가져오기 로직 비동기 구현 필요
    ...

@app.get("/get/all-name-sq")
async def web_get_name_sq():
    # 모든 아파트 이름과 평형 반환 로직 비동기 구현 필요
    ...

@app.get("/get/all-name")
async def web_get_name():
    # 모든 아파트 이름 반환 로직 비동기 구현 필요
    ...

@app.post("/get_answers")
async def get_answers(request: Request):
    data = await request.json()
    # OpenAI GPT API 호출 로직 비동기 구현 필요
    ...

@app.post("/search")
async def search_apt(request: Request):
    data = await request.json()
    # 아파트 검색 로직 비동기 구현 필요
    ...

@app.get("/")
async def initial_request():
    return {"success": "initial request"}