"""
Config: Baseline
Descripción: Configuración por defecto del sistema. Sirve como referencia.

  content_weight       = 0.70  → predomina la afinidad de contenido
  serendipity_weight   = 0.15  → exploración moderada
  game_score_weight    = 0.05  → leve influencia del score global del juego
"""

NAME = "Baseline"
DESCRIPTION = "Configuración por defecto"

PARAMS = {
    "RECOMMENDATION_CONTENT_WEIGHT":    0.70,
    "RECOMMENDATION_SERENDIPITY_WEIGHT": 0.15,
    "RECOMMENDATION_GAME_SCORE_WEIGHT":  0.05,
    "SERENDIPITY_TARGET_CONTENT_SCORE":  0.35,
    "SERENDIPITY_ALLOWED_DEVIATION":     0.15,
}
