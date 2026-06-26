"""
Config: High Content
Descripción: Prioriza fuertemente la afinidad de contenido (géneros).
             El componente colaborativo queda en su mínimo permitido.
             Esperable: alta precisión por género, menor diversidad.

  content_weight       = 0.70
  collab_weight        = 0.10  (implícito)
  serendipity_weight   = 0.10
  game_score_weight    = 0.10
"""

NAME = "High Content"
DESCRIPTION = "Máximo peso en afinidad de contenido"

PARAMS = {
    "RECOMMENDATION_CONTENT_WEIGHT":    0.70,
    "RECOMMENDATION_SERENDIPITY_WEIGHT": 0.10,
    "RECOMMENDATION_GAME_SCORE_WEIGHT":  0.10,
    "SERENDIPITY_TARGET_CONTENT_SCORE":  0.35,
    "SERENDIPITY_ALLOWED_DEVIATION":     0.15,
}
