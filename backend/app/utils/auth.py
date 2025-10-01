import jwt
import datetime
from functools import wraps
from flask import request, jsonify
from config import Config
from app.utils.database import db


def generate_jwt_token(user_id):
    """生成 JWT token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=Config.JWT_EXPIRATION_HOURS),
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)
    return token


def decode_jwt_token(token):
    """解碼 JWT token"""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """JWT token 驗證裝飾器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # 從 Authorization header 獲取 token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        # 解碼 token
        payload = decode_jwt_token(token)
        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401

        # 獲取用戶信息
        user = db.execute_query(
            "SELECT * FROM Users WHERE user_id = ?",
            (payload['user_id'],),
            fetch_one=True
        )

        if not user:
            return jsonify({'error': 'User not found'}), 401

        # 將用戶信息添加到請求上下文
        request.current_user = user

        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    """管理員權限驗證裝飾器"""
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if not request.current_user.get('is_admin'):
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)

    return decorated
