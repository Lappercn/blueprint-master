# 文件名：config.py
"""
功能说明：应用配置加载
核心功能：从环境变量加载配置
依赖模块：os, dotenv
"""
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class Config:
    # TextIn OCR 配置
    TEXTIN_APP_ID = os.getenv("TEXTIN_APP_ID")
    TEXTIN_SECRET_CODE = os.getenv("TEXTIN_SECRET_CODE")
    
    # OpenAI/Doubao 配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
    LLM_MODEL = os.getenv("LLM_MODEL")

    # MongoDB 配置
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/blueprint_master")
    
    @staticmethod
    def init_app(app):
        pass
