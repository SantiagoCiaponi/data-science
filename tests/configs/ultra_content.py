"""
Config: Ultra Content
Descripción: Lleva el componente de contenido al extremo (δ=0.95).
             Prácticamente elimina el componente colaborativo y minimiza serendipia.
             Se utiliza para validar si subir δ más allá de High Content (0.90) sigue
             mejorando las métricas o si el sistema comienza a perder efectividad.

  content_weight       = 0.95
  serendipity_weight   = 0.03
  game_score_weight    = 0.02
"""

NAME = "Ultra Content"
DESCRIPTION = "Extremo de afinidad de contenido para validar límite de High Content"

PARAMS = {
    "RECOMMENDATION_CONTENT_WEIGHT":    0.95,
    "RECOMMENDATION_SERENDIPITY_WEIGHT": 0.03,
    "RECOMMENDATION_GAME_SCORE_WEIGHT":  0.02,
    "SERENDIPITY_TARGET_CONTENT_SCORE":  0.35,
    "SERENDIPITY_ALLOWED_DEVIATION":     0.15,
}
