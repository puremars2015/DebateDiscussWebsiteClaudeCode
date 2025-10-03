from flask import Blueprint, request, jsonify, redirect
import requests
from urllib.parse import urlencode
from config import Config
from app.utils.database import db
from app.utils.auth import generate_jwt_token

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET'])
def login():
    """重定向到 Line Login 授權頁面"""
    params = {
        'response_type': 'code',
        'client_id': Config.LINE_CHANNEL_ID,
        'redirect_uri': Config.LINE_CALLBACK_URL,
        'state': 'random_state_string',  # 實際應用中應該使用隨機生成的 state
        'scope': 'profile openid'
    }
    auth_url = f"{Config.LINE_AUTH_URL}?{urlencode(params)}"
    return jsonify({'auth_url': auth_url})


@bp.route('/callback', methods=['GET'])
def callback():
    """Line Login 回調處理"""
    code = request.args.get('code')
    state = request.args.get('state')

    if not code:
        return jsonify({'error': 'Authorization code not provided'}), 400

    # 交換 access token
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': Config.LINE_CALLBACK_URL,
        'client_id': Config.LINE_CHANNEL_ID,
        'client_secret': Config.LINE_CHANNEL_SECRET
    }

    try:
        token_response = requests.post(Config.LINE_TOKEN_URL, data=token_data)
        token_response.raise_for_status()
        token_json = token_response.json()
        access_token = token_json.get('access_token')

        # 獲取用戶資料
        headers = {'Authorization': f'Bearer {access_token}'}
        profile_response = requests.get(Config.LINE_PROFILE_URL, headers=headers)
        profile_response.raise_for_status()
        profile = profile_response.json()

        # 檢查用戶是否已存在
        user = db.execute_query(
            "SELECT * FROM Users WHERE line_id = ?",
            (profile['userId'],),
            fetch_one=True
        )

        if user:
            # 更新用戶資料
            db.execute_query(
                """
                UPDATE Users
                SET nickname = ?, avatar = ?, updated_at = GETDATE()
                WHERE user_id = ?
                """,
                (profile.get('displayName'), profile.get('pictureUrl'), user['user_id'])
            )
            user_id = user['user_id']
        else:
            # 創建新用戶
            user_id = db.execute_insert(
                """
                INSERT INTO Users (line_id, nickname, avatar)
                VALUES (?, ?, ?)
                """,
                (profile['userId'], profile.get('displayName'), profile.get('pictureUrl'))
            )

        # 生成 JWT token
        jwt_token = generate_jwt_token(user_id)

        # 重定向到前端登入頁面，帶上 token 和使用者資料參數
        from urllib.parse import urlencode
        params = {
            'token': jwt_token,
            'user_id': user_id,
            'nickname': profile.get('displayName', ''),
            'avatar': profile.get('pictureUrl', '')
        }
        frontend_url = f"{Config.FRONTEND_URL}/pages/login.html?{urlencode(params)}"
        return redirect(frontend_url)

    except requests.RequestException as e:
        return jsonify({'error': 'Failed to authenticate with Line'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/verify', methods=['GET'])
def verify():
    """驗證 JWT token"""
    from app.utils.auth import token_required

    @token_required
    def _verify():
        return jsonify({
            'valid': True,
            'user': {
                'user_id': request.current_user['user_id'],
                'nickname': request.current_user['nickname'],
                'avatar': request.current_user['avatar'],
                'rating': request.current_user['rating'],
                'is_admin': request.current_user['is_admin']
            }
        })

    return _verify()
