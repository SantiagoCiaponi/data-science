"""
Config: High Content
Descripción: Prioriza fuertemente la afinidad de contenido (géneros).
             El componente colaborativo tiene poco peso.
             Esperable: alta precisión por género, menor diversidad.

  content_weight       = 0.90
  serendipity_weight   = 0.08
  game_score_weight    = 0.02
"""

NAME = "High Content"
DESCRIPTION = "Máximo peso en afinidad de contenido"

PARAMS = {
    "RECOMMENDATION_CONTENT_WEIGHT":    0.90,
    "RECOMMENDATION_SERENDIPITY_WEIGHT": 0.08,
    "RECOMMENDATION_GAME_SCORE_WEIGHT":  0.02,
    "SERENDIPITY_TARGET_CONTENT_SCORE":  0.35,
    "SERENDIPITY_ALLOWED_DEVIATION":     0.15,
}
