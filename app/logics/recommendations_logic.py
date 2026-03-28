import math
import random
import pandas as pd
import config
from ..models import Item, User
from .games_logic import build_item_from_row, get_game_feature_vector, read_games_df
from .preferences_logic import get_preferences_for_item, get_rated_item_ids_for_user
from .users_logic import build_user_from_row, get_csv_user, get_user_preference_vector, read_users_df

# Devuelve los k juegos mejor puntuados que el usuario todavía no calificó
def get_k_recommendations(user_id: int, k: int) -> list[Item]:
    # Obtenemos: usuario, juegos calificados y todos los juegos
    user = get_csv_user(user_id)
    rated_item_ids = get_rated_item_ids_for_user(user_id)
    games_df = read_games_df()

    # Lista donde vamos a guardar (score_calculado, fila_del_juego)
    scored_games = []
    # Recorremos todos los juegos y vamos guardando los scores de cada juego para el usuario
    for _, game_row in games_df.iterrows():
        game_id = int(game_row[config.GAME_ID_COLUMN])

        # Si el usuario ya calificó este juego, lo salteamos
        if game_id in rated_item_ids:
            continue

        # Calculamos score_contenido + score_colaborativo
        final_score = get_final_score(user, game_row)

        scored_games.append(
            {
                "score": final_score,
                "row": game_row,
            }
        )

    # Ordenamos los juegos de mayor a menor score_calculado
    scored_games.sort(key=lambda game_data: game_data["score"], reverse=True)

    candidate_pool = scored_games[:max(k, k * 2)]
    selected_games = get_random_recommendation_sample(candidate_pool, k)

    recommended_items: list[Item] = []
    for game_data in selected_games:
        recommended_items.append(build_item_from_row(game_data["row"]))

    return recommended_items

# Combina el score basado en contenido, el score colaborativo, el score de serendipia y el score global del juego
def get_final_score(user: User, game_row: pd.Series) -> float:
    content_score = get_content_score(user, game_row)
    collaborative_score = get_collaborative_score(user, int(game_row[config.GAME_ID_COLUMN]))
    base_score = get_base_score(content_score, collaborative_score)

    serendipity_score = get_serendipity_score(content_score, game_row)
    beta = config.RECOMMENDATION_SERENDIPITY_WEIGHT
    combined_recommendation_score = (1 - beta) * base_score + beta * serendipity_score

    game_score = get_game_score(game_row)
    gamma = config.RECOMMENDATION_GAME_SCORE_WEIGHT

    return (1 - gamma) * combined_recommendation_score + gamma * game_score

# Calcula el score basado en contenido entre un usuario y un juego
# score_contenido(u, i) representa la afinidad entre ambos vectores
def get_content_score(user: User, game_row: pd.Series) -> float:
    user_vector = get_user_preference_vector(user)
    game_vector = get_game_feature_vector(game_row)
    return cosine_similarity(user_vector, game_vector)

def get_base_score(content_score: float, collaborative_score: float) -> float:
    alpha = config.RECOMMENDATION_CONTENT_WEIGHT
    return alpha * content_score + (1 - alpha) * collaborative_score

# g(r) diferencia valoraciones negativas, neutras y positivas
def transform_collaborative_ranking(ranking: int) -> float:
    return config.COLLABORATIVE_RANKING_MAP.get(ranking, 0.0)

# Calcula la similitud entre el usuario objetivo y otro usuario
def get_similarity_between_users(target_user: User, other_user: User) -> float:
    target_user_vector = get_user_preference_vector(target_user)
    other_user_vector = get_user_preference_vector(other_user)
    return cosine_similarity(target_user_vector, other_user_vector)

# Score Serendipia: Juegos moderadamente afines pero no obvios y con buena userscore
def get_serendipity_score(content_score: float, game_row: pd.Series) -> float:
    mid_table_score = get_mid_table_affinity_score(content_score)
    game_score = get_game_score(game_row)
    serendipity_score = (
        config.SERENDIPITY_MID_TABLE_WEIGHT * mid_table_score + 
        config.SERENDIPITY_GAME_SCORE_WEIGHT * game_score
    )
    return clamp_score(serendipity_score)

# Obtiene una lista de preferencias del usuario modificada que nos ayude a encontrar juegos moderadamente afines
def get_mid_table_affinity_score(content_score: float) -> float:
    target_score = config.SERENDIPITY_TARGET_CONTENT_SCORE
    allowed_deviation = max(config.SERENDIPITY_ALLOWED_DEVIATION, 0.0001)
    distance_to_target = abs(clamp_score(content_score) - target_score)
    return clamp_score(1.0 - (distance_to_target / allowed_deviation))

# Usa el userscore del juego como una señal global de calidad para favorecer juegos bien recibidos por la comunidad
def get_game_score(game_row: pd.Series) -> float:
    userscore = float(game_row.get(config.GAME_USERSCORE_COLUMN, 0.0)) / 100.0
    return clamp_score(userscore)

def clamp_score(value: float) -> float:
    return max(0.0, min(1.0, value))

# Calcula el score colaborativo de un juego para un usuario
# Qué tanto le gustó ese juego a otros usuarios, ponderado por la similitud entre ambos usuarios
def get_collaborative_score(user: User, game_id: int) -> float:
    # Buscamos todas las preferencias cargadas para este juego
    game_preferences = get_preferences_for_item(game_id)

    # Si nadie puntuó este juego, no hay score colaborativo
    if game_preferences.empty:
        return 0.0

    # Leemos todos los usuarios
    users_df = read_users_df()

    total_weighted_score = 0.0
    total_similarity = 0.0

    # Recorremos cada preferencia hecha sobre este juego, buscamos al usuario qué hizo la review
    # calculamos similitud y acumulamos el score ponderado
    for _, preference in game_preferences.iterrows():
        other_user_id = int(preference[config.PREFERENCE_USER_ID_COLUMN])

        # Ignoramos al mismo usuario
        if other_user_id == user.id:
            continue

        # Buscamos la fila del otro usuario
        matching_rows = users_df[
            users_df[config.USER_ID_COLUMN] == other_user_id
        ]

        # Si no encontramos al usuario, seguimos con el próximo
        if matching_rows.empty:
            continue

        # Ya que encontramos otro usuario que hizo una reivew, tomamos la fila del usuario
        other_user_row = matching_rows.iloc[0]
        other_user = build_user_from_row(other_user_row)

        # Calculamos similitud entre ambos usuarios
        similarity = get_similarity_between_users(user, other_user)

        # Obtenemos y transformamos el ranking del otro usuario para este juego
        ranking = int(float(preference[config.PREFERENCE_RANKING_COLUMN]))
        transformed_ranking = transform_collaborative_ranking(ranking)

        # Calculamos el aporte de este usuario
        weighted_score = similarity * transformed_ranking

        # Acumulamos
        total_weighted_score += weighted_score
        total_similarity += abs(similarity)

    if total_similarity == 0:
        return 0.0

    # Score final
    collaborative_score = total_weighted_score / total_similarity
    return collaborative_score

# Nos ayuda a obtener una muestra aleatoria de juegos recomendados para agregar diversidad a las recomendaciones 
def get_random_recommendation_sample(candidate_pool: list[dict[str, object]],k: int) -> list[dict[str, object]]:
    if k <= 0 or not candidate_pool:
        return []

    sample_size = min(k, len(candidate_pool))
    return random.sample(candidate_pool, sample_size)

# Operaciones matemáticas
def cosine_similarity(left: list[float], right: list[float]) -> float:
    left_norm = vector_norm(left)
    right_norm = vector_norm(right)
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot_product(left, right) / (left_norm * right_norm)

def dot_product(left: list[float], right: list[float]) -> float:
    total = 0.0
    for index in range(min(len(left), len(right))):
        total += left[index] * right[index]

    return total

def vector_norm(values: list[float]) -> float:
    total = 0.0
    for value in values:
        total += value * value

    return math.sqrt(total)
