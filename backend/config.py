import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # 數據庫配置
    DB_SERVER = os.getenv('DB_SERVER', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'DebatePlatform')
    DB_USER = os.getenv('DB_USER', '')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')

    # 構建連接字符串
    DB_CONNECTION_STRING = (
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={DB_SERVER};'
        f'DATABASE={DB_NAME};'
        f'UID={DB_USER};'
        f'PWD={DB_PASSWORD}'
    )

    # JWT 配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))

    # Line Login 配置
    LINE_CHANNEL_ID = os.getenv('LINE_CHANNEL_ID', '')
    LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', '')
    LINE_CALLBACK_URL = os.getenv('LINE_CALLBACK_URL', 'http://localhost:5000/api/auth/callback')

    # Line API URLs
    LINE_AUTH_URL = 'https://access.line.me/oauth2/v2.1/authorize'
    LINE_TOKEN_URL = 'https://api.line.me/oauth2/v2.1/token'
    LINE_PROFILE_URL = 'https://api.line.me/v2/profile'

    # Flask 配置
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    PORT = int(os.getenv('PORT', 5000))

    # Elo 評分配置
    ELO_K_FACTOR = 32
    INITIAL_RATING = 1500

    # 辯論配置
    MAX_ROUNDS = 5
    INSTANT_WIN_PERCENTAGE = 0.70  # 70% 得票率即時獲勝
    CONSECUTIVE_WINS_FOR_VICTORY = 3  # 連續 3 輪獲勝
    DEFAULT_VOTING_HOURS = 24
    JUDGE_VOTE_WEIGHT = 10
    REGULAR_VOTE_WEIGHT = 1
