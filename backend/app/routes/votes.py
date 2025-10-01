from flask import Blueprint, request, jsonify
from config import Config
from app.utils.database import db
from app.utils.auth import token_required
from app.utils.elo import calculate_elo, get_score_from_result

bp = Blueprint('votes', __name__)


@bp.route('/<int:round_id>/vote', methods=['POST'])
@token_required
def submit_vote(round_id):
    """提交投票"""
    data = request.get_json()
    side_voted = data.get('side_voted')  # 'pros' or 'cons'

    if side_voted not in ['pros', 'cons']:
        return jsonify({'error': 'Invalid side_voted value'}), 400

    # 獲取回合信息
    round_data = db.execute_query(
        "SELECT * FROM Rounds WHERE round_id = ?",
        (round_id,),
        fetch_one=True
    )

    if not round_data:
        return jsonify({'error': 'Round not found'}), 404

    if round_data['status'] != 'WAIT_VOTING':
        return jsonify({'error': 'Voting is not open for this round'}), 400

    # 檢查用戶是否已投票
    existing_vote = db.execute_query(
        "SELECT * FROM Votes WHERE round_id = ? AND voter_id = ?",
        (round_id, request.current_user['user_id']),
        fetch_one=True
    )

    if existing_vote:
        return jsonify({'error': 'You have already voted in this round'}), 400

    # 檢查用戶是否為法官
    debate = db.execute_query(
        "SELECT * FROM Debates WHERE debate_id = ?",
        (round_data['debate_id'],),
        fetch_one=True
    )

    is_judge = db.execute_query(
        "SELECT * FROM JudgeAssignments WHERE debate_id = ? AND user_id = ?",
        (debate['debate_id'], request.current_user['user_id']),
        fetch_one=True
    ) is not None

    # 設置投票權重
    weight = Config.JUDGE_VOTE_WEIGHT if is_judge else Config.REGULAR_VOTE_WEIGHT

    # 插入投票
    db.execute_insert(
        """
        INSERT INTO Votes (round_id, voter_id, side_voted, is_judge, weight)
        VALUES (?, ?, ?, ?, ?)
        """,
        (round_id, request.current_user['user_id'], side_voted, is_judge, weight)
    )

    return jsonify({'message': 'Vote submitted successfully'})


@bp.route('/<int:round_id>/results', methods=['GET'])
def get_voting_results(round_id):
    """獲取投票結果"""
    round_data = db.execute_query(
        "SELECT * FROM Rounds WHERE round_id = ?",
        (round_id,),
        fetch_one=True
    )

    if not round_data:
        return jsonify({'error': 'Round not found'}), 404

    if round_data['status'] not in ['VOTING_CLOSED', 'ROUND_RESULT']:
        return jsonify({'error': 'Voting results not available yet'}), 400

    # 統計投票
    vote_stats = db.execute_query(
        """
        SELECT side_voted, SUM(weight) as total_votes, COUNT(*) as vote_count
        FROM Votes
        WHERE round_id = ?
        GROUP BY side_voted
        """,
        (round_id,),
        fetch_all=True
    )

    pros_votes = 0
    cons_votes = 0

    for stat in vote_stats:
        if stat['side_voted'] == 'pros':
            pros_votes = stat['total_votes']
        elif stat['side_voted'] == 'cons':
            cons_votes = stat['total_votes']

    total_votes = pros_votes + cons_votes

    if total_votes > 0:
        pros_percentage = (pros_votes / total_votes) * 100
        cons_percentage = (cons_votes / total_votes) * 100
    else:
        pros_percentage = 0
        cons_percentage = 0

    return jsonify({
        'round_id': round_id,
        'pros_votes': pros_votes,
        'cons_votes': cons_votes,
        'total_votes': total_votes,
        'pros_percentage': round(pros_percentage, 2),
        'cons_percentage': round(cons_percentage, 2),
        'winner_side': round_data.get('winner_side')
    })


@bp.route('/<int:round_id>/close_voting', methods=['POST'])
def close_voting(round_id):
    """關閉投票並計算結果（可由定時任務調用）"""
    round_data = db.execute_query(
        "SELECT * FROM Rounds WHERE round_id = ?",
        (round_id,),
        fetch_one=True
    )

    if not round_data or round_data['status'] != 'WAIT_VOTING':
        return jsonify({'error': 'Invalid round status'}), 400

    # 統計投票
    vote_stats = db.execute_query(
        """
        SELECT side_voted, SUM(weight) as total_votes
        FROM Votes
        WHERE round_id = ?
        GROUP BY side_voted
        """,
        (round_id,),
        fetch_all=True
    )

    pros_votes = 0
    cons_votes = 0

    for stat in vote_stats:
        if stat['side_voted'] == 'pros':
            pros_votes = stat['total_votes']
        elif stat['side_voted'] == 'cons':
            cons_votes = stat['total_votes']

    total_votes = pros_votes + cons_votes

    # 確定勝者
    winner_side = None
    if total_votes > 0:
        pros_percentage = pros_votes / total_votes
        cons_percentage = cons_votes / total_votes

        if pros_percentage >= Config.INSTANT_WIN_PERCENTAGE:
            winner_side = 'pros'
        elif cons_percentage >= Config.INSTANT_WIN_PERCENTAGE:
            winner_side = 'cons'
        elif pros_votes > cons_votes:
            winner_side = 'pros'
        elif cons_votes > pros_votes:
            winner_side = 'cons'
        else:
            winner_side = 'draw'

    # 更新回合狀態
    db.execute_query(
        "UPDATE Rounds SET status = 'ROUND_RESULT', winner_side = ? WHERE round_id = ?",
        (winner_side, round_id)
    )

    # 獲取辯論信息
    debate = db.execute_query(
        "SELECT * FROM Debates WHERE debate_id = ?",
        (round_data['debate_id'],),
        fetch_one=True
    )

    # 更新連勝計數
    if winner_side == 'pros':
        new_pros_wins = debate['pros_consecutive_wins'] + 1
        new_cons_wins = 0
    elif winner_side == 'cons':
        new_pros_wins = 0
        new_cons_wins = debate['cons_consecutive_wins'] + 1
    else:
        new_pros_wins = 0
        new_cons_wins = 0

    db.execute_query(
        """
        UPDATE Debates
        SET pros_consecutive_wins = ?, cons_consecutive_wins = ?
        WHERE debate_id = ?
        """,
        (new_pros_wins, new_cons_wins, debate['debate_id'])
    )

    # 檢查勝利條件
    debate_finished = False
    final_winner_id = None

    # 檢查即時獲勝（70%以上得票率）
    if total_votes > 0 and (pros_percentage >= Config.INSTANT_WIN_PERCENTAGE or cons_percentage >= Config.INSTANT_WIN_PERCENTAGE):
        debate_finished = True
        final_winner_id = debate['pros_user_id'] if winner_side == 'pros' else debate['cons_user_id']

    # 檢查連勝3局
    elif new_pros_wins >= Config.CONSECUTIVE_WINS_FOR_VICTORY:
        debate_finished = True
        final_winner_id = debate['pros_user_id']

    elif new_cons_wins >= Config.CONSECUTIVE_WINS_FOR_VICTORY:
        debate_finished = True
        final_winner_id = debate['cons_user_id']

    # 檢查是否達到最大回合數
    elif round_data['round_number'] >= Config.MAX_ROUNDS:
        debate_finished = True
        # 需要管理員手動判定

    if debate_finished and final_winner_id:
        # 更新辯論狀態
        db.execute_query(
            "UPDATE Debates SET status = 'FINISHED', winner_id = ? WHERE debate_id = ?",
            (final_winner_id, debate['debate_id'])
        )

        # 更新 Elo 評分
        update_player_ratings(debate)

    elif not debate_finished:
        # 創建新回合
        new_round_number = round_data['round_number'] + 1
        db.execute_insert(
            """
            INSERT INTO Rounds (debate_id, round_number, status)
            VALUES (?, ?, 'WAIT_PROS_STATEMENT')
            """,
            (debate['debate_id'], new_round_number)
        )

        db.execute_query(
            "UPDATE Debates SET round_count = ? WHERE debate_id = ?",
            (new_round_number, debate['debate_id'])
        )

    return jsonify({
        'message': 'Voting closed',
        'winner_side': winner_side,
        'debate_finished': debate_finished
    })


def update_player_ratings(debate):
    """更新玩家 Elo 評分"""
    # 獲取玩家當前評分
    pros_user = db.execute_query(
        "SELECT * FROM Users WHERE user_id = ?",
        (debate['pros_user_id'],),
        fetch_one=True
    )

    cons_user = db.execute_query(
        "SELECT * FROM Users WHERE user_id = ?",
        (debate['cons_user_id'],),
        fetch_one=True
    )

    pros_rating_before = pros_user['rating']
    cons_rating_before = cons_user['rating']

    # 確定勝負
    if debate['winner_id'] == debate['pros_user_id']:
        pros_result = 'win'
        cons_result = 'loss'
        pros_score = 1.0
        cons_score = 0.0
    elif debate['winner_id'] == debate['cons_user_id']:
        pros_result = 'loss'
        cons_result = 'win'
        pros_score = 0.0
        cons_score = 1.0
    else:
        pros_result = 'draw'
        cons_result = 'draw'
        pros_score = 0.5
        cons_score = 0.5

    # 計算新評分
    pros_rating_after, cons_rating_after = calculate_elo(
        pros_rating_before,
        cons_rating_before,
        pros_score,
        cons_score
    )

    # 更新用戶評分和戰績
    if pros_result == 'win':
        db.execute_query(
            "UPDATE Users SET rating = ?, wins = wins + 1 WHERE user_id = ?",
            (pros_rating_after, debate['pros_user_id'])
        )
    elif pros_result == 'loss':
        db.execute_query(
            "UPDATE Users SET rating = ?, losses = losses + 1 WHERE user_id = ?",
            (pros_rating_after, debate['pros_user_id'])
        )
    else:
        db.execute_query(
            "UPDATE Users SET rating = ?, draws = draws + 1 WHERE user_id = ?",
            (pros_rating_after, debate['pros_user_id'])
        )

    if cons_result == 'win':
        db.execute_query(
            "UPDATE Users SET rating = ?, wins = wins + 1 WHERE user_id = ?",
            (cons_rating_after, debate['cons_user_id'])
        )
    elif cons_result == 'loss':
        db.execute_query(
            "UPDATE Users SET rating = ?, losses = losses + 1 WHERE user_id = ?",
            (cons_rating_after, debate['cons_user_id'])
        )
    else:
        db.execute_query(
            "UPDATE Users SET rating = ?, draws = draws + 1 WHERE user_id = ?",
            (cons_rating_after, debate['cons_user_id'])
        )

    # 記錄比賽歷史
    db.execute_insert(
        """
        INSERT INTO MatchHistory (debate_id, user_id, result, rating_before, rating_after)
        VALUES (?, ?, ?, ?, ?)
        """,
        (debate['debate_id'], debate['pros_user_id'], pros_result, pros_rating_before, pros_rating_after)
    )

    db.execute_insert(
        """
        INSERT INTO MatchHistory (debate_id, user_id, result, rating_before, rating_after)
        VALUES (?, ?, ?, ?, ?)
        """,
        (debate['debate_id'], debate['cons_user_id'], cons_result, cons_rating_before, cons_rating_after)
    )
