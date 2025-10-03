from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from config import Config
import os

app = Flask(__name__)

# 禁用 URL 尾部斜線的嚴格匹配，避免不必要的重定向
app.url_map.strict_slashes = False

# 簡單的 CORS 配置 - 開發環境允許所有來源
CORS(app, resources={r"/*": {"origins": "*"}})

# 導入路由
from app.routes import auth, users, topics, debates, rounds, votes, ranking, admin

# 註冊藍圖
app.register_blueprint(auth.bp, url_prefix='/api/auth')
app.register_blueprint(users.bp, url_prefix='/api/users')
app.register_blueprint(topics.bp, url_prefix='/api/topics')
app.register_blueprint(debates.bp, url_prefix='/api/debates')
app.register_blueprint(rounds.bp, url_prefix='/api/rounds')
app.register_blueprint(votes.bp, url_prefix='/api/votes')
app.register_blueprint(ranking.bp, url_prefix='/api/ranking')
app.register_blueprint(admin.bp, url_prefix='/api/admin')


# 靜態文件路由 - 提供前端文件
@app.route('/pages/<path:filename>')
def serve_pages(filename):
    frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'pages')
    return send_from_directory(frontend_dir, filename)


@app.route('/static/<path:subpath>')
def serve_static(subpath):
    # 處理 /static/css/*, /static/js/* 等路徑
    frontend_static_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static')
    return send_from_directory(frontend_static_dir, subpath)


@app.route('/')
def index():
    # 重定向到登入頁面
    from flask import redirect
    return redirect('/pages/login.html')


@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=Config.PORT,
        debug=True
    )
