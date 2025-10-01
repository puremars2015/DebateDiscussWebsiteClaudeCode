from config import Config


def calculate_elo(rating_a, rating_b, score_a, score_b):
    """
    計算 Elo 評分

    Args:
        rating_a: 玩家 A 的當前評分
        rating_b: 玩家 B 的當前評分
        score_a: 玩家 A 的得分 (1=贏, 0.5=平局, 0=輸)
        score_b: 玩家 B 的得分 (1=贏, 0.5=平局, 0=輸)

    Returns:
        tuple: (new_rating_a, new_rating_b)
    """
    k = Config.ELO_K_FACTOR

    # 計算期望勝率
    expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    expected_b = 1 / (1 + 10 ** ((rating_a - rating_b) / 400))

    # 計算新評分
    new_a = rating_a + k * (score_a - expected_a)
    new_b = rating_b + k * (score_b - expected_b)

    return round(new_a), round(new_b)


def get_score_from_result(result):
    """
    將比賽結果轉換為得分

    Args:
        result: 'win', 'loss', 'draw'

    Returns:
        float: 得分值
    """
    result_map = {
        'win': 1.0,
        'draw': 0.5,
        'loss': 0.0
    }
    return result_map.get(result, 0.0)
