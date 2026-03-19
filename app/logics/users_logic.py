import pandas as pd
import config
from pandas.errors import EmptyDataError
from ..exceptions import UserNotFoundException
from ..models import User, UserAttributes, UserCreationDTO

# Crea el csv de usuarios si no existe
def initialize_users_storage() -> None:
    try:
        pd.read_csv(config.USERS_CSV)
    except (FileNotFoundError, EmptyDataError):
        pd.DataFrame(columns=config.USER_COLUMNS).to_csv(config.USERS_CSV, index=False)

# Devuelve todos los usuarios en formato DataFrame
def read_users_df() -> pd.DataFrame:
    return pd.read_csv(config.USERS_CSV)

# Guarda el csv de usuarios a partir de un DataFrame
def save_users_df(df: pd.DataFrame) -> None:
    df.to_csv(config.USERS_CSV, index=False)

# Mapeamos un User a partir de una fila del DataFrame
def build_user_from_row(row: pd.Series) -> User:
    return User(
        id=int(row[config.USER_ID_COLUMN]),
        username=row[config.USERNAME_COLUMN],
        attributes=UserAttributes(
            **{
                column: float(row[column])
                for column in config.USER_ATTRIBUTE_COLUMNS
            }
        ),
    )

# Devuelve un usuario a partir de su ID
def get_csv_user(user_id: int) -> User:
    df = read_users_df()
    user_row = df[df[config.USER_ID_COLUMN] == user_id]

    if user_row.empty:
        raise UserNotFoundException(user_id)

    return build_user_from_row(user_row.iloc[0])

# Obtiene el proximo ID a insertar en la tabla de usuarios
def get_next_user_id() -> int:
    df = read_users_df()

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
    user_id = get_next_user_id()

    new_user_row = {
        config.USER_ID_COLUMN: user_id,
        config.USERNAME_COLUMN: payload.username,
        **payload.attributes.model_dump(),
    }

    df = pd.concat([df, pd.DataFrame([new_user_row])], ignore_index=True)
    save_users_df(df)

    return User(id=user_id, username=payload.username, attributes=payload.attributes)

# Actualiza las preferencias de un usuario a partir de un juego y un ranking dado por el usuario
def update_user_preferences_from_game(user_id: int, game_row, ranking: int) -> None:
    df = read_users_df()
    user_index = df.index[df[config.USER_ID_COLUMN] == user_id]

    if len(user_index) == 0:
        raise UserNotFoundException(user_id)

    idx = user_index[0]
    ranking_weight = config.RANKING_WEIGHT_MAP.get(ranking, 0.0)

    for game_column, user_column in config.GAME_TO_USER_ATTRIBUTE_MAP.items():
        game_value = float(game_row.get(game_column, 0))
        current_value = float(df.at[idx, user_column])
        new_value = get_new_user_preference_value(current_value, game_value, ranking)
        df.at[idx, user_column] = new_value

    save_users_df(df)
    
# Limita el valor de una preferencia al rango permitido
def clamp_preference(value: float) -> float:
    return max(config.PREFERENCE_MIN_VALUE, min(config.PREFERENCE_MAX_VALUE, value))

def get_new_user_preference_value (current_value: float, game_value: float, ranking: int) -> float:
    ranking_weight = config.RANKING_WEIGHT_MAP.get(ranking, 0.0)
    # u_i = clamp(u_i + alpha * f(r) * x_i)
    return clamp_preference(current_value + config.PREFERENCE_UPDATE_ALPHA * ranking_weight * game_value)
    
# Obtiene el vector de preferencias de un usuario
def get_user_preference_vector(user: User) -> list[float]:
    attributes = user.attributes.model_dump()
    return [float(attributes[column]) for column in config.USER_ATTRIBUTE_COLUMNS]