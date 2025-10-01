from flask import Blueprint, request, jsonify
from app.utils.database import db
from app.utils.auth import admin_required

bp = Blueprint('admin', __name__)


@bp.route('/topics/pending', methods=['GET'])
@admin_required
def get_pending_topics():
    """獲取待審核的話題"""
    topics = db.execute_query(
        """
        SELECT t.*, u.nickname as creator_nickname
        FROM DebateTopics t
        JOIN Users u ON t.created_by = u.user_id
        WHERE t.status = 'pending'
        ORDER BY t.created_at DESC
        """,
        fetch_all=True
    )

    return jsonify({'topics': topics})


@bp.route('/topics/<int:topic_id>/approve', methods=['POST'])
@admin_required
def approve_topic(topic_id):
    """批准話題"""
    topic = db.execute_query(
        "SELECT * FROM DebateTopics WHERE topic_id = ?",
        (topic_id,),
        fetch_one=True
    )

    if not topic:
        return jsonify({'error': 'Topic not found'}), 404

    if topic['status'] != 'pending':
        return jsonify({'error': 'Topic is not pending approval'}), 400

    db.execute_query(
        "UPDATE DebateTopics SET status = 'approved', updated_at = GETDATE() WHERE topic_id = ?",
        (topic_id,)
    )

    return jsonify({'message': 'Topic approved successfully'})


@bp.route('/topics/<int:topic_id>/reject', methods=['POST'])
@admin_required
def reject_topic(topic_id):
    """拒絕話題"""
    topic = db.execute_query(
        "SELECT * FROM DebateTopics WHERE topic_id = ?",
        (topic_id,),
        fetch_one=True
    )

    if not topic:
        return jsonify({'error': 'Topic not found'}), 404

    if topic['status'] != 'pending':
        return jsonify({'error': 'Topic is not pending approval'}), 400

    db.execute_query(
        "UPDATE DebateTopics SET status = 'rejected', updated_at = GETDATE() WHERE topic_id = ?",
        (topic_id,)
    )

    return jsonify({'message': 'Topic rejected successfully'})


@bp.route('/debates/<int:debate_id>/force_end', methods=['POST'])
@admin_required
def force_end_debate(debate_id):
    """強制結束辯論並判定勝者（用於達到最大回合數的情況）"""
    data = request.get_json()
    winner_id = data.get('winner_id')  # 可以為 null 表示平局

    debate = db.execute_query(
        "SELECT * FROM Debates WHERE debate_id = ?",
        (debate_id,),
        fetch_one=True
    )

    if not debate:
        return jsonify({'error': 'Debate not found'}), 404

    if debate['status'] == 'FINISHED':
        return jsonify({'error': 'Debate is already finished'}), 400

    # 驗證 winner_id
    if winner_id and winner_id not in [debate['pros_user_id'], debate['cons_user_id']]:
        return jsonify({'error': 'Invalid winner_id'}), 400

    # 更新辯論狀態
    db.execute_query(
        "UPDATE Debates SET status = 'FINISHED', winner_id = ? WHERE debate_id = ?",
        (winner_id, debate_id)
    )

    # 如果有勝者，更新 Elo 評分
    if winner_id:
        from app.routes.votes import update_player_ratings
        debate['winner_id'] = winner_id  # 更新 winner_id
        update_player_ratings(debate)

    return jsonify({'message': 'Debate ended successfully'})


@bp.route('/users/<int:user_id>/set_admin', methods=['POST'])
@admin_required
def set_admin(user_id):
    """設置用戶為管理員"""
    data = request.get_json()
    is_admin = data.get('is_admin', True)

    user = db.execute_query(
        "SELECT * FROM Users WHERE user_id = ?",
        (user_id,),
        fetch_one=True
    )

    if not user:
        return jsonify({'error': 'User not found'}), 404

    db.execute_query(
        "UPDATE Users SET is_admin = ? WHERE user_id = ?",
        (is_admin, user_id)
    )

    return jsonify({'message': 'User admin status updated successfully'})


@bp.route('/judges/assign', methods=['POST'])
@admin_required
def assign_judge():
    """為辯論分配法官"""
    data = request.get_json()
    debate_id = data.get('debate_id')
    user_id = data.get('user_id')

    if not all([debate_id, user_id]):
        return jsonify({'error': 'Missing required fields'}), 400

    # 檢查辯論是否存在
    debate = db.execute_query(
        "SELECT * FROM Debates WHERE debate_id = ?",
        (debate_id,),
        fetch_one=True
    )

    if not debate:
        return jsonify({'error': 'Debate not found'}), 404

    # 檢查用戶是否存在
    user = db.execute_query(
        "SELECT * FROM Users WHERE user_id = ?",
        (user_id,),
        fetch_one=True
    )

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # 檢查用戶是否為辯論參與者
    if user_id in [debate['pros_user_id'], debate['cons_user_id']]:
        return jsonify({'error': 'Debaters cannot be judges'}), 400

    # 檢查是否已分配
    existing = db.execute_query(
        "SELECT * FROM JudgeAssignments WHERE debate_id = ? AND user_id = ?",
        (debate_id, user_id),
        fetch_one=True
    )

    if existing:
        return jsonify({'error': 'Judge already assigned'}), 400

    # 分配法官
    db.execute_insert(
        "INSERT INTO JudgeAssignments (debate_id, user_id) VALUES (?, ?)",
        (debate_id, user_id)
    )

    return jsonify({'message': 'Judge assigned successfully'})
