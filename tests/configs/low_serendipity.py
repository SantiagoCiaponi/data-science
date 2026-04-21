"""
Config: Low Serendipity
Descripción: Minimiza la serendipia para obtener recomendaciones más predecibles
             y ajustadas al perfil del usuario.
             Esperable: máxima precisión por género, menor cobertura.

  content_weight       = 0.70
  serendipity_weight   = 0.04
  game_score_weight    = 0.06
"""

NAME = "Low Serendipity"
DESCRIPTION = "Recomendaciones predecibles, sin exploración"

PARAMS = {
    "RECOMMENDATION_CONTENT_WEIGHT":    0.70,
    "RECOMMENDATION_SERENDIPITY_WEIGHT": 0.04,
    "RECOMMENDATION_GAME_SCORE_WEIGHT":  0.06,
    "SERENDIPITY_TARGET_CONTENT_SCORE":  0.35,
    "SERENDIPITY_ALLOWED_DEVIATION":     0.15,
}
