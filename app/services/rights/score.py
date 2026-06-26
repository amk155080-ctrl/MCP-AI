"""
MCP16 Rights Score Engine

권리분석 결과를 100점 만점 점수로 환산하는 모듈.
향후 MCP16.6에서 고도화 예정.
"""


def calculate_rights_score(risk_score: float = 0.0) -> float:
    score = 100.0 - float(risk_score)

    if score < 0:
        return 0.0

    if score > 100:
        return 100.0

    return score
