"""
Config: High Serendipity
Descripción: Aumenta el peso de la serendipia para explorar ítems menos obvios.
             Busca ampliar la cobertura del catálogo y sorprender al usuario.
             Esperable: mayor cobertura, menor precisión por género.

  content_weight       = 0.65
  serendipity_weight   = 0.30
  game_score_weight    = 0.05
"""

NAME = "High Serendipity"
DESCRIPTION = "Mayor exploración mediante serendipia"

PARAMS = {
    "RECOMMENDATION_CONTENT_WEIGHT":    0.65,
    "RECOMMENDATION_SERENDIPITY_WEIGHT": 0.30,
    "RECOMMENDATION_GAME_SCORE_WEIGHT":  0.05,
    "SERENDIPITY_TARGET_CONTENT_SCORE":  0.40,
    "SERENDIPITY_ALLOWED_DEVIATION":     0.20,
}
