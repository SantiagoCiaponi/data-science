import pandas as pd
import config
from ..models import PreferenceCreateDTO, PreferenceCreatedResponse
from .games_logic import get_game_row
from .users_logic import get_csv_user, update_user_preferences_from_game

# Devuelve todas las preferencias en formato DataFrame
def read_preferences_df() -> pd.DataFrame:
    return pd.read_csv(config.PREFERENCES_CSV)

# Guarda el csv de preferencias a partir de un DataFrame
def save_preferences_df(df: pd.DataFrame) -> None:
    df.to_csv(config.PREFERENCES_CSV, index=False)

# Devuelve todas las preferencias hechas sobre un juego
def get_preferences_for_item(item_id: int) -> pd.DataFrame:
    df = read_preferences_df()
    return df[df[config.PREFERENCE_ITEM_ID_COLUMN] == item_id]

# Devuelve los IDs de juegos que un usuario ya calificó
def get_rated_item_ids_for_user(user_id: int) -> set[int]:
    df = read_preferences_df()
    user_preferences = df[df[config.PREFERENCE_USER_ID_COLUMN] == user_id]
    if user_preferences.empty:
        return set()

    item_ids = pd.to_numeric(
        user_preferences[config.PREFERENCE_ITEM_ID_COLUMN],
        errors="coerce",
    ).dropna()
    return {int(item_id) for item_id in item_ids.tolist()}

# Guarda una preferencia y actualiza el perfil del usuario
def create_preference(payload: PreferenceCreateDTO) -> PreferenceCreatedResponse:
    user = get_csv_user(payload.user_id)
    selected_game = get_game_row(payload.item_id)

    df = read_preferences_df()
    new_preference_row = {
        config.PREFERENCE_USER_ID_COLUMN: user.id,
        config.PREFERENCE_ITEM_ID_COLUMN: payload.item_id,
        config.PREFERENCE_RANKING_COLUMN: payload.ranking,
    }

    df = pd.concat([df, pd.DataFrame([new_preference_row])], ignore_index=True)
    save_preferences_df(df)

    update_user_preferences_from_game(user.id, selected_game, payload.ranking)
    updated_user = get_csv_user(user.id)

    return PreferenceCreatedResponse(
        message="Preferencia registrada y perfil actualizado",
        userId=user.id,
        itemId=payload.item_id,
        ranking=payload.ranking,
        updatedAttributes=updated_user.attributes,
    )
