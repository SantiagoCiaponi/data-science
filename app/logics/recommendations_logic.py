import math
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

        scored_games.append((final_score, game_row))

    # Ordenamos los juegos de mayor a menor score_calculado
    scored_games.sort(key=lambda game_data: game_data[0], reverse=True)

    # Tomamos los primeros k juegos y los convertimos a Item
    return [
        build_item_from_row(game_row)
        for _, game_row in scored_games[:k]
    ]

# Combina el score basado en contenido y el score colaborativo
# score_final(u, i) = alpha * score_contenido(u, i) + (1 - alpha) * score_colaborativo(u, i)
def get_final_score(user: User, game_row: pd.Series) -> float:
    content_score = get_content_score(user, game_row)
    collaborative_score = get_collaborative_score(user, int(game_row[config.GAME_ID_COLUMN]))
    alpha = config.RECOMMENDATION_CONTENT_WEIGHT
    return alpha * content_score + (1 - alpha) * collaborative_score

# Calcula el score basado en contenido entre un usuario y un juego
# score_contenido(u, i) representa la afinidad entre ambos vectores
def get_content_score(user: User, game_row: pd.Series) -> float:
    user_vector = get_user_preference_vector(user)
    game_vector = get_game_feature_vector(game_row)
    return cosine_similarity(user_vector, game_vector)

# g(r) diferencia valoraciones negativas, neutras y positivas
def transform_collaborative_ranking(ranking: int) -> float:
    return config.COLLABORATIVE_RANKING_MAP.get(ranking, 0.0)

# Calcula el score colaborativo de un juego para un usuario
# score_colaborativo(u, i) = sum(sim(u,v) * g(r_v_i)) / sum(|sim(u,v)|)
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

# Calcula la similitud entre el usuario objetivo y otro usuario
def get_similarity_between_users(target_user: User, other_user: User) -> float:
    return cosine_similarity(
        get_user_preference_vector(target_user),
        get_user_preference_vector(other_user),
    )

# Operaciones matemáticas
def cosine_similarity(left: list[float], right: list[float]) -> float:
    left_norm = vector_norm(left)
    right_norm = vector_norm(right)
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot_product(left, right) / (left_norm * right_norm)

def dot_product(left: list[float], right: list[float]) -> float:
    return sum(left_value * right_value for left_value, right_value in zip(left, right))

def vector_norm(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values))

