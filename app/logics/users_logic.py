import pandas as pd
import config
from pandas.errors import EmptyDataError
from ..exceptions import UserNotFoundException
from ..models import User, UserAttributes, UserCreationDTO

def initialize_users_storage() -> None:
    try:
        pd.read_csv(config.USERS_CSV)
    except (FileNotFoundError, EmptyDataError):
        pd.DataFrame(columns=config.USER_COLUMNS).to_csv(config.USERS_CSV, index=False)

def read_users_df() -> pd.DataFrame:
    return pd.read_csv(config.USERS_CSV)

def save_users_df(df: pd.DataFrame) -> None:
    df.to_csv(config.USERS_CSV, index=False)

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

def get_csv_user(user_id: int) -> User:
    df = read_users_df()
    user_row = df[df[config.USER_ID_COLUMN] == user_id]

    if user_row.empty:
        raise UserNotFoundException(user_id)

    return build_user_from_row(user_row.iloc[0])

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

def clamp_preference(value: float) -> float:
    return max(config.PREFERENCE_MIN_VALUE, min(config.PREFERENCE_MAX_VALUE, value))

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
        new_value = clamp_preference(
            current_value + config.PREFERENCE_UPDATE_ALPHA * ranking_weight * game_value
        )
        df.at[idx, user_column] = new_value

    save_users_df(df)