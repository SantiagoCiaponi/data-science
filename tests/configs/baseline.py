"""
Config: Baseline
Descripción: Configuración por defecto del sistema. Sirve como referencia.

  content_weight       = 0.55  → predomina la afinidad de contenido
  collab_weight        = 0.20  → influencia moderada de usuarios similares (implícito)
  serendipity_weight   = 0.15  → exploración moderada
  game_score_weight    = 0.10  → leve influencia del score global del juego
"""

NAME = "Baseline"
DESCRIPTION = "Configuración por defecto"

PARAMS = {
    "RECOMMENDATION_CONTENT_WEIGHT":    0.55,
    "RECOMMENDATION_SERENDIPITY_WEIGHT": 0.15,
    "RECOMMENDATION_GAME_SCORE_WEIGHT":  0.10,
    "SERENDIPITY_TARGET_CONTENT_SCORE":  0.35,
    "SERENDIPITY_ALLOWED_DEVIATION":     0.15,
}
