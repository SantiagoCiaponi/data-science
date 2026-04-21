"""
Config: Balanced
Descripción: Reparte de forma más equitativa el peso entre contenido,
             colaborativo y serendipia.
             Esperable: métricas intermedias y equilibradas entre arquetipos.

  content_weight       = 0.55
  serendipity_weight   = 0.20
  game_score_weight    = 0.05
"""

NAME = "Balanced"
DESCRIPTION = "Equilibrio entre contenido, colaborativo y serendipia"

PARAMS = {
    "RECOMMENDATION_CONTENT_WEIGHT":    0.55,
    "RECOMMENDATION_SERENDIPITY_WEIGHT": 0.20,
    "RECOMMENDATION_GAME_SCORE_WEIGHT":  0.05,
    "SERENDIPITY_TARGET_CONTENT_SCORE":  0.35,
    "SERENDIPITY_ALLOWED_DEVIATION":     0.15,
}
