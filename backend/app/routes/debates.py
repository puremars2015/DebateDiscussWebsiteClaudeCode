from flask import Blueprint, request, jsonify
from app.utils.database import db
from app.utils.auth import token_required, admin_required

bp = Blueprint('debates', __name__)


@bp.route('/', methods=['GET'])
def get_debates():
    """獲取辯論列表"""
    status = request.args.get('status', 'ONGOING')

    debates = db.execute_query(
        """
        SELECT d.*, dt.title as topic_title,
               pu.nickname as pros_nickname, cu.nickname as cons_nickname
        FROM Debates d
        JOIN DebateTopics dt ON d.topic_id = dt.topic_id
        JOIN Users pu ON d.pros_user_id = pu.user_id
        JOIN Users cu ON d.cons_user_id = cu.user_id
        WHERE d.status = ?
        ORDER BY d.created_at DESC
        """,
        (status,),
        fetch_all=True
    )

    return jsonify({'debates': debates})


@bp.route('/<int:debate_id>', methods=['GET'])
def get_debate(debate_id):
    """獲取辯論詳情"""
    debate = db.execute_query(
        """
        SELECT d.*, dt.title as topic_title, dt.description as topic_description,
               dt.side_pros, dt.side_cons,
               pu.nickname as pros_nickname, pu.avatar as pros_avatar, pu.rating as pros_rating,
               cu.nickname as cons_nickname, cu.avatar as cons_avatar, cu.rating as cons_rating
        FROM Debates d
        JOIN DebateTopics dt ON d.topic_id = dt.topic_id
        JOIN Users pu ON d.pros_user_id = pu.user_id
        JOIN Users cu ON d.cons_user_id = cu.user_id
        WHERE d.debate_id = ?
        """,
        (debate_id,),
        fetch_one=True
    )

    if not debate:
        return jsonify({'error': 'Debate not found'}), 404

    # 獲取所有回合
    rounds = db.execute_query(
        """
        SELECT * FROM Rounds
        WHERE debate_id = ?
        ORDER BY round_number
        """,
        (debate_id,),
        fetch_all=True
    )

    debate['rounds'] = rounds

    return jsonify(debate)


@bp.route('/create', methods=['POST'])
@admin_required
def create_debate():
    """創建新辯論（管理員）"""
    data = request.get_json()

    topic_id = data.get('topic_id')
    pros_user_id = data.get('pros_user_id')
    cons_user_id = data.get('cons_user_id')

    if not all([topic_id, pros_user_id, cons_user_id]):
        return jsonify({'error': 'Missing required fields'}), 400

    if pros_user_id == cons_user_id:
        return jsonify({'error': 'Pros and cons users must be different'}), 400

    # 檢查話題是否已批准
    topic = db.execute_query(
        "SELECT * FROM DebateTopics WHERE topic_id = ? AND status = 'approved'",
        (topic_id,),
        fetch_one=True
    )

    if not topic:
        return jsonify({'error': 'Topic not found or not approved'}), 404

    # 創建辯論
    debate_id = db.execute_insert(
        """
        INSERT INTO Debates (topic_id, pros_user_id, cons_user_id, status)
        VALUES (?, ?, ?, 'ONGOING')
        """,
        (topic_id, pros_user_id, cons_user_id)
    )

    # 創建第一回合
    round_id = db.execute_insert(
        """
        INSERT INTO Rounds (debate_id, round_number, status)
        VALUES (?, 1, 'WAIT_PROS_STATEMENT')
        """,
        (debate_id,)
    )

    # 更新辯論回合數
    db.execute_query(
        "UPDATE Debates SET round_count = 1 WHERE debate_id = ?",
        (debate_id,)
    )

    return jsonify({
        'message': 'Debate created successfully',
        'debate_id': debate_id,
        'round_id': round_id
    }), 201
