from flask import Flask, jsonify
from flask_cors import CORS
from config import Config

app = Flask(__name__)
CORS(app)

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


@app.route('/')
def index():
    return jsonify({
        'message': 'Debate Platform API',
        'version': '1.0.0',
        'status': 'running'
    })


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
        debug=Config.DEBUG
    )
