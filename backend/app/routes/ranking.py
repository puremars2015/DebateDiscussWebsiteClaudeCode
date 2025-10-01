from flask import Blueprint, jsonify
from app.utils.database import db

bp = Blueprint('ranking', __name__)


@bp.route('/', methods=['GET'])
def get_ranking():
    """獲取排行榜"""
    users = db.execute_query(
        """
        SELECT user_id, nickname, avatar, rating, wins, losses, draws,
               CASE
                   WHEN (wins + losses + draws) > 0
                   THEN CAST(wins AS FLOAT) / (wins + losses + draws) * 100
                   ELSE 0
               END as win_rate
        FROM Users
        WHERE (wins + losses + draws) > 0
        ORDER BY rating DESC, wins DESC
        """,
        fetch_all=True
    )

    # 添加排名
    for i, user in enumerate(users):
        user['rank'] = i + 1
        user['win_rate'] = round(user['win_rate'], 2)

    return jsonify({'ranking': users})
