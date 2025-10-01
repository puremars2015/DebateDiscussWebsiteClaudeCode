from flask import Blueprint, request, jsonify
from app.utils.database import db
from app.utils.auth import token_required

bp = Blueprint('users', __name__)


@bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """獲取當前用戶資料"""
    user = request.current_user
    return jsonify({
        'user_id': user['user_id'],
        'nickname': user['nickname'],
        'avatar': user['avatar'],
        'rating': user['rating'],
        'wins': user['wins'],
        'losses': user['losses'],
        'draws': user['draws'],
        'is_admin': user['is_admin']
    })


@bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """獲取指定用戶的公開資料"""
    user = db.execute_query(
        "SELECT user_id, nickname, avatar, rating, wins, losses, draws FROM Users WHERE user_id = ?",
        (user_id,),
        fetch_one=True
    )

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify(user)


@bp.route('/<int:user_id>/matches', methods=['GET'])
def get_user_matches(user_id):
    """獲取用戶的比賽歷史"""
    matches = db.execute_query(
        """
        SELECT mh.*, d.topic_id, dt.title as topic_title,
               CASE
                   WHEN d.pros_user_id = ? THEN d.cons_user_id
                   ELSE d.pros_user_id
               END as opponent_id,
               CASE
                   WHEN d.pros_user_id = ? THEN cu.nickname
                   ELSE pu.nickname
               END as opponent_nickname
        FROM MatchHistory mh
        JOIN Debates d ON mh.debate_id = d.debate_id
        JOIN DebateTopics dt ON d.topic_id = dt.topic_id
        LEFT JOIN Users pu ON d.pros_user_id = pu.user_id
        LEFT JOIN Users cu ON d.cons_user_id = cu.user_id
        WHERE mh.user_id = ?
        ORDER BY mh.created_at DESC
        """,
        (user_id, user_id, user_id),
        fetch_all=True
    )

    return jsonify({'matches': matches})
