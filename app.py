# 실행방법: uvicorn fast_api:app --reload --host 127.0.0.1 --port 5000
import asyncio

from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from db_models import AptReview, AptTrade, AptInfo
from config import config
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import selectinload
import httpx
import sys

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
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


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
async def web_getdata(apt_code: str, apt_name: str, db: AsyncSession = Depends(get_db)):
    if not apt_code or not apt_name:
        raise HTTPException(status_code=400, detail="Please provide both apt_code and apt_name")

    # Fetch apt_review data
    result = await db.execute(select(AptReview).filter_by(apt_code=apt_code))
    reviews = result.scalars().all()
    review_list = [
        {'category': review.category, 'review': review.review}
        for review in reviews
    ]

    # Fetch apt_trade data
    result = await db.execute(select(AptTrade).filter_by(apt_code=apt_code))
    trades = result.scalars().all()
    trade_list = [
        {
            'apt_sq': trade.apt_sq, 'avg_price': trade.avg_price,
            'top_avg_price': trade.top_avg_price, 'bottom_avg_price': trade.bottom_avg_price,
            'recent_avg': trade.recent_avg, 'recent_top': trade.recent_top,
            'recent_bottom': trade.recent_bottom, 'trade_trend': trade.trade_trend,
            'price_trend': trade.price_trend
        }
        for trade in trades
    ]

    # Return the data as JSON
    return {
        'apt_code': apt_code,
        'apt_name': apt_name,
        'reviews': review_list,
        'trades': trade_list
    }


@app.get("/get/all-name-sq")
async def web_get_name_sq(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AptInfo.apt_name, AptTrade.apt_sq)
        .join(AptTrade, AptInfo.apt_code == AptTrade.apt_code)
    )
    results = result.all()

    name_sq_list = [
        {
            "apt_name": apt_name,
            "apt_sq": f"{apt_sq}㎡"
        }
        for apt_name, apt_sq in results
    ]

    return {"name_and_sq": name_sq_list}


@app.get("/get/all-name")
async def web_get_name(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AptInfo.apt_name))
    results = result.scalars().all()

    name_list = [{"apt_name": name} for name in results]

    return name_list


@app.post("/get_answers")
async def get_answers(request: Request):
    data = await request.json()
    if not data or 'message' not in data:
        raise HTTPException(status_code=400, detail="No 'message' provided in request.")

    provided_string = data['message']

    # OpenAI GPT-4를 호출하는 비동기 함수를 정의합니다.
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {constants.APIKEY}"
            },
            json={
                "model": "gpt-4",
                "messages": [
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
            }
        )
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error calling OpenAI API")

    qna_pairs = [{"answer": ans["message"]["content"]} for ans in response.json()["choices"]]

    return qna_pairs


@app.post("/search")
async def search_apt(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    if not data or 'message' not in data:
        raise HTTPException(status_code=400, detail="No 'message' provided in request.")

    provided_string = data['message']

    if len(provided_string) == 1:
        result = await db.execute(select(AptInfo).filter(AptInfo.apt_name.like(f"%{provided_string}%")))
    else:
        case_statements = [case((AptInfo.apt_name.like(f'%{char}%'), 1), else_=0) for char in provided_string]

        score_column = func.coalesce(sum(case_statements), 0).label('score')
        query = select(AptInfo, score_column).filter(score_column > 0).order_by(score_column.desc())
        result = await db.execute(query)

    apartments = result.all()
    apartment_list = [
        {"apt_code": apt[0].apt_code, "apt_name": apt[0].apt_name}
        for apt in apartments
    ]

    return apartment_list


# 로드밸런서의 테스트를 위한 기본 응답
@app.get("/")
async def initial_request():
    return {"success": "initial request"}


if __name__ == '__main__':
    py_ver = int(f"{sys.version_info.major}{sys.version_info.minor}")
    if py_ver > 37 and sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
