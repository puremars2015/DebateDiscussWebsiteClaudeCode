from flask import Blueprint, request, jsonify
import json
import datetime
from config import Config
from app.utils.database import db
from app.utils.auth import token_required

bp = Blueprint('rounds', __name__)


def check_user_permission(debate, user_id, required_side):
    """檢查用戶是否有權限操作"""
    if required_side == 'pros' and debate['pros_user_id'] != user_id:
        return False
    if required_side == 'cons' and debate['cons_user_id'] != user_id:
        return False
    return True


def advance_round_state(round_id, current_status, debate_id):
    """推進回合狀態"""
    state_flow = {
        'WAIT_PROS_STATEMENT': 'WAIT_CONS_QUESTIONS',
        'WAIT_CONS_QUESTIONS': 'WAIT_PROS_REPLY',
        'WAIT_PROS_REPLY': 'WAIT_CONS_STATEMENT',
        'WAIT_CONS_STATEMENT': 'WAIT_PROS_QUESTIONS',
        'WAIT_PROS_QUESTIONS': 'WAIT_CONS_REPLY',
        'WAIT_CONS_REPLY': 'WAIT_VOTING'
    }

    next_status = state_flow.get(current_status)

    if next_status:
        if next_status == 'WAIT_VOTING':
            # 設置投票截止時間
            deadline = datetime.datetime.now() + datetime.timedelta(hours=Config.DEFAULT_VOTING_HOURS)
            db.execute_query(
                "UPDATE Rounds SET status = ?, voting_deadline = ? WHERE round_id = ?",
                (next_status, deadline, round_id)
            )
        else:
            db.execute_query(
                "UPDATE Rounds SET status = ? WHERE round_id = ?",
                (next_status, round_id)
            )


@bp.route('/<int:round_id>', methods=['GET'])
def get_round(round_id):
    """獲取回合詳情"""
    round_data = db.execute_query(
        "SELECT * FROM Rounds WHERE round_id = ?",
        (round_id,),
        fetch_one=True
    )

    if not round_data:
        return jsonify({'error': 'Round not found'}), 404

    # 解析 JSON 數據
    if round_data.get('cons_questions'):
        try:
            round_data['cons_questions'] = json.loads(round_data['cons_questions'])
        except:
            round_data['cons_questions'] = []

    if round_data.get('pros_questions'):
        try:
            round_data['pros_questions'] = json.loads(round_data['pros_questions'])
        except:
            round_data['pros_questions'] = []

    return jsonify(round_data)


@bp.route('/<int:round_id>/pros_statement', methods=['POST'])
@token_required
def submit_pros_statement(round_id):
    """正方提交主張"""
    data = request.get_json()
    statement = data.get('statement')

    if not statement:
        return jsonify({'error': 'Statement is required'}), 400

    # 獲取回合和辯論信息
    round_data = db.execute_query(
        "SELECT * FROM Rounds WHERE round_id = ?",
        (round_id,),
        fetch_one=True
    )

    if not round_data:
        return jsonify({'error': 'Round not found'}), 404

    if round_data['status'] != 'WAIT_PROS_STATEMENT':
        return jsonify({'error': 'Invalid round status'}), 400

    # 獲取辯論信息
    debate = db.execute_query(
        "SELECT * FROM Debates WHERE debate_id = ?",
        (round_data['debate_id'],),
        fetch_one=True
    )

    if not check_user_permission(debate, request.current_user['user_id'], 'pros'):
        return jsonify({'error': 'Permission denied'}), 403

    # 更新回合
    db.execute_query(
        "UPDATE Rounds SET pros_statement = ? WHERE round_id = ?",
        (statement, round_id)
    )

    # 推進狀態
    advance_round_state(round_id, 'WAIT_PROS_STATEMENT', debate['debate_id'])

    return jsonify({'message': 'Statement submitted successfully'})


@bp.route('/<int:round_id>/cons_questions', methods=['POST'])
@token_required
def submit_cons_questions(round_id):
    """反方提交質詢"""
    data = request.get_json()
    questions = data.get('questions')

    if not questions or not isinstance(questions, list):
        return jsonify({'error': 'Questions must be a list'}), 400

    round_data = db.execute_query(
        "SELECT * FROM Rounds WHERE round_id = ?",
        (round_id,),
        fetch_one=True
    )

    if not round_data or round_data['status'] != 'WAIT_CONS_QUESTIONS':
        return jsonify({'error': 'Invalid round status'}), 400

    debate = db.execute_query(
        "SELECT * FROM Debates WHERE debate_id = ?",
        (round_data['debate_id'],),
        fetch_one=True
    )

    if not check_user_permission(debate, request.current_user['user_id'], 'cons'):
        return jsonify({'error': 'Permission denied'}), 403

    questions_json = json.dumps(questions, ensure_ascii=False)
    db.execute_query(
        "UPDATE Rounds SET cons_questions = ? WHERE round_id = ?",
        (questions_json, round_id)
    )

    advance_round_state(round_id, 'WAIT_CONS_QUESTIONS', debate['debate_id'])

    return jsonify({'message': 'Questions submitted successfully'})


@bp.route('/<int:round_id>/pros_reply', methods=['POST'])
@token_required
def submit_pros_reply(round_id):
    """正方回覆質詢"""
    data = request.get_json()
    reply = data.get('reply')

    if not reply:
        return jsonify({'error': 'Reply is required'}), 400

    round_data = db.execute_query(
        "SELECT * FROM Rounds WHERE round_id = ?",
        (round_id,),
        fetch_one=True
    )

    if not round_data or round_data['status'] != 'WAIT_PROS_REPLY':
        return jsonify({'error': 'Invalid round status'}), 400

    debate = db.execute_query(
        "SELECT * FROM Debates WHERE debate_id = ?",
        (round_data['debate_id'],),
        fetch_one=True
    )

    if not check_user_permission(debate, request.current_user['user_id'], 'pros'):
        return jsonify({'error': 'Permission denied'}), 403

    db.execute_query(
        "UPDATE Rounds SET pros_reply = ? WHERE round_id = ?",
        (reply, round_id)
    )

    advance_round_state(round_id, 'WAIT_PROS_REPLY', debate['debate_id'])

    return jsonify({'message': 'Reply submitted successfully'})


@bp.route('/<int:round_id>/cons_statement', methods=['POST'])
@token_required
def submit_cons_statement(round_id):
    """反方提交主張"""
    data = request.get_json()
    statement = data.get('statement')

    if not statement:
        return jsonify({'error': 'Statement is required'}), 400

    round_data = db.execute_query(
        "SELECT * FROM Rounds WHERE round_id = ?",
        (round_id,),
        fetch_one=True
    )

    if not round_data or round_data['status'] != 'WAIT_CONS_STATEMENT':
        return jsonify({'error': 'Invalid round status'}), 400

    debate = db.execute_query(
        "SELECT * FROM Debates WHERE debate_id = ?",
        (round_data['debate_id'],),
        fetch_one=True
    )

    if not check_user_permission(debate, request.current_user['user_id'], 'cons'):
        return jsonify({'error': 'Permission denied'}), 403

    db.execute_query(
        "UPDATE Rounds SET cons_statement = ? WHERE round_id = ?",
        (statement, round_id)
    )

    advance_round_state(round_id, 'WAIT_CONS_STATEMENT', debate['debate_id'])

    return jsonify({'message': 'Statement submitted successfully'})


@bp.route('/<int:round_id>/pros_questions', methods=['POST'])
@token_required
def submit_pros_questions(round_id):
    """正方提交質詢"""
    data = request.get_json()
    questions = data.get('questions')

    if not questions or not isinstance(questions, list):
        return jsonify({'error': 'Questions must be a list'}), 400

    round_data = db.execute_query(
        "SELECT * FROM Rounds WHERE round_id = ?",
        (round_id,),
        fetch_one=True
    )

    if not round_data or round_data['status'] != 'WAIT_PROS_QUESTIONS':
        return jsonify({'error': 'Invalid round status'}), 400

    debate = db.execute_query(
        "SELECT * FROM Debates WHERE debate_id = ?",
        (round_data['debate_id'],),
        fetch_one=True
    )

    if not check_user_permission(debate, request.current_user['user_id'], 'pros'):
        return jsonify({'error': 'Permission denied'}), 403

    questions_json = json.dumps(questions, ensure_ascii=False)
    db.execute_query(
        "UPDATE Rounds SET pros_questions = ? WHERE round_id = ?",
        (questions_json, round_id)
    )

    advance_round_state(round_id, 'WAIT_PROS_QUESTIONS', debate['debate_id'])

    return jsonify({'message': 'Questions submitted successfully'})


@bp.route('/<int:round_id>/cons_reply', methods=['POST'])
@token_required
def submit_cons_reply(round_id):
    """反方回覆質詢"""
    data = request.get_json()
    reply = data.get('reply')

    if not reply:
        return jsonify({'error': 'Reply is required'}), 400

    round_data = db.execute_query(
        "SELECT * FROM Rounds WHERE round_id = ?",
        (round_id,),
        fetch_one=True
    )

    if not round_data or round_data['status'] != 'WAIT_CONS_REPLY':
        return jsonify({'error': 'Invalid round status'}), 400

    debate = db.execute_query(
        "SELECT * FROM Debates WHERE debate_id = ?",
        (round_data['debate_id'],),
        fetch_one=True
    )

    if not check_user_permission(debate, request.current_user['user_id'], 'cons'):
        return jsonify({'error': 'Permission denied'}), 403

    db.execute_query(
        "UPDATE Rounds SET cons_reply = ? WHERE round_id = ?",
        (reply, round_id)
    )

    advance_round_state(round_id, 'WAIT_CONS_REPLY', debate['debate_id'])

    return jsonify({'message': 'Reply submitted successfully'})
