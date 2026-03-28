import pandas as pd
import config
from ..exceptions import UserNotFoundException
from ..models import User, UserAttributes, UserCreationDTO

# Devuelve todos los usuarios en formato DataFrame
def read_users_df() -> pd.DataFrame:
    return pd.read_csv(config.USERS_CSV)

# Guarda el csv de usuarios a partir de un DataFrame
def save_users_df(df: pd.DataFrame) -> None:
    df.to_csv(config.USERS_CSV, index=False)

# Genera un diccionario con todas las preferencias inicializadas en 0
def get_empty_user_attributes() -> dict[str, float]:
    return {column: 0.0 for column in config.get_user_attribute_columns()}

# Completa las preferencias faltantes y convierte los valores a float
def sanitize_user_attributes(raw_attributes: UserAttributes | dict[str, float]) -> dict[str, float]:
    if isinstance(raw_attributes, UserAttributes):
        raw_attributes = raw_attributes.model_dump()

    sanitized_attributes = get_empty_user_attributes()
    for column in sanitized_attributes:
        if column in raw_attributes:
            sanitized_attributes[column] = float(raw_attributes[column])
    return sanitized_attributes

# Lee si un juego tiene activado un género one-hot en su fila
def get_game_genre_value(game_row: pd.Series, genre_name: str) -> float:
    column_name = config.get_genre_column_name(genre_name)
    return float(float(game_row.get(column_name, 0)) > 0)

# Mapeamos un User a partir de una fila del DataFrame
def build_user_from_row(row: pd.Series) -> User:
    return User(
        id=int(row[config.USER_ID_COLUMN]),
        username=row[config.USERNAME_COLUMN],
        attributes={
            column: float(row.get(column, 0.0))
            for column in config.get_user_attribute_columns()
        },
    )

# Devuelve un usuario a partir de su ID
def get_csv_user(user_id: int) -> User:
    df = read_users_df()
    user_row = df[df[config.USER_ID_COLUMN] == user_id]

    if user_row.empty:
        raise UserNotFoundException(user_id)

    return build_user_from_row(user_row.iloc[0])

# Obtiene el proximo ID a insertar en la tabla de usuarios
def get_next_user_id(df: pd.DataFrame) -> int:
    if df.empty or config.USER_ID_COLUMN not in df.columns:
        return 1

    ids = pd.to_numeric(df[config.USER_ID_COLUMN], errors="coerce").dropna().astype(int)
    if ids.empty:
        return 1

    used = set(ids.tolist())
    new_id = 1
    while new_id in used:
        new_id += 1

    return new_id

# Guardamos un Usuario en el csv de usuarios.
def create_user(payload: UserCreationDTO) -> User:
    df = read_users_df()
    user_id = get_next_user_id(df)
    sanitized_attributes = sanitize_user_attributes(payload.attributes)

    new_user_row = {
        config.USER_ID_COLUMN: user_id,
        config.USERNAME_COLUMN: payload.username,
        **sanitized_attributes,
    }

    df = pd.concat([df, pd.DataFrame([new_user_row])], ignore_index=True)
    save_users_df(df)

    return User(id=user_id, username=payload.username, attributes=sanitized_attributes)

# Actualiza las preferencias de un usuario a partir de un juego y un ranking dado por el usuario
def update_user_preferences_from_game(user_id: int, game_row, ranking: int) -> None:
    df = read_users_df()
    user_index = df.index[df[config.USER_ID_COLUMN] == user_id]

    if len(user_index) == 0:
        raise UserNotFoundException(user_id)

    idx = user_index[0]

    for genre_name, user_column in config.get_game_to_user_attribute_map().items():
        game_value = get_game_genre_value(game_row, genre_name)
        current_value = float(df.at[idx, user_column])
        new_value = get_new_user_preference_value(current_value, game_value, ranking)
        df.at[idx, user_column] = new_value

    save_users_df(df)

# Limita el valor de una preferencia al rango permitido
def clamp_preference(value: float) -> float:
    return max(config.PREFERENCE_MIN_VALUE, min(config.PREFERENCE_MAX_VALUE, value))

# Calcula el nuevo valor de una preferencia según el ranking dado
def get_new_user_preference_value(current_value: float, game_value: float, ranking: int) -> float:
    ranking_weight = config.RANKING_WEIGHT_MAP.get(ranking, 0.0)
    return clamp_preference(current_value + config.PREFERENCE_UPDATE_ALPHA * ranking_weight * game_value)

# Obtiene el vector de preferencias de un usuario
def get_user_preference_vector(user: User) -> list[float]:
    return [
        float(getattr(user.attributes, column))
        for column in config.get_user_attribute_columns()
    ]
