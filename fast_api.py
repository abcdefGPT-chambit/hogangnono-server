from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from db_models import db, AptReview, AptTrade, AptInfo
from config import config
import openai
from sqlalchemy import case, func
# GPT API 설정
import constants

app = FastAPI()

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 오리진 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드 허용
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

