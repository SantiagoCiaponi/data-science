"""
Config: High Collaborative
Descripción: Reduce el peso del contenido para dar más relevancia a la
             señal colaborativa (qué valoraron usuarios similares).
             Esperable: recomendaciones más influenciadas por la comunidad,
             potencialmente menor precisión por género si los vecinos son mixtos.

  content_weight       = 0.15
  collab_weight        = 0.65  (implícito)
  serendipity_weight   = 0.10
  game_score_weight    = 0.10
"""

NAME = "High Collab"
DESCRIPTION = "Mayor peso en filtrado colaborativo"

PARAMS = {
    "RECOMMENDATION_CONTENT_WEIGHT":    0.15,
    "RECOMMENDATION_SERENDIPITY_WEIGHT": 0.10,
    "RECOMMENDATION_GAME_SCORE_WEIGHT":  0.10,
    "SERENDIPITY_TARGET_CONTENT_SCORE":  0.35,
    "SERENDIPITY_ALLOWED_DEVIATION":     0.15,
}
