import pandas as pd

from .exceptions import UserNotFoundException
from .models import User
from config import CSV_FILE

def get_csv_user(user_id: int) -> User:
    df = pd.read_csv(CSV_FILE)
    user_row = df[df["id"] == user_id]

    if user_row.empty:
        raise UserNotFoundException(user_id)

    row = user_row.iloc[0]

    return User(
        id=int(row["id"]),
        username=row["username"],
        attributes={
            "open_world_action_preference": float(row["open_world_action_preference"]),
            "fps_preference": float(row["fps_preference"]),
            "survival_preference": float(row["survival_preference"]),
            "action_rpg_preference": float(row["action_rpg_preference"]),
            "linear_action_adventure_preference": float(row["linear_action_adventure_preference"]),
        },
    )

def get_next_user_id() -> int:
    df = pd.read_csv(CSV_FILE)

    if df.empty or "id" not in df.columns:
        return 1

    ids = pd.to_numeric(df["id"], errors="coerce").dropna().astype(int)
    if ids.empty:
        return 1

    used = set(ids.tolist())
    new_id = 1
    while new_id in used:
        new_id += 1

    return new_id

def clamp_preference(value: float) -> float:
    return max(0.0, min(10.0, value))

def update_user_preferences_from_game(user_id: int, game_row, ranking: int) -> None:
    df = pd.read_csv(CSV_FILE)
    user_index = df.index[df["id"] == user_id]

    if len(user_index) == 0:
        raise UserNotFoundException(user_id)

    idx = user_index[0]

    ranking_delta_map = {
        1: -0.5,
        2: -0.25,
        3: 0.0,
        4: 0.25,
        5: 0.5,
    }

    delta = ranking_delta_map.get(ranking, 0.0)

    game_to_user_map = {
        "open_world_action": "open_world_action_preference",
        "fps": "fps_preference",
        "survival": "survival_preference",
        "action_rpg": "action_rpg_preference",
        "linear_action_adventure": "linear_action_adventure_preference",
    }

    for game_col, user_col in game_to_user_map.items():
        game_value = float(game_row.get(game_col, 0))
        current_value = float(df.at[idx, user_col])
        new_value = clamp_preference(current_value + delta * game_value)
        df.at[idx, user_col] = new_value

    df.to_csv(CSV_FILE, index=False)