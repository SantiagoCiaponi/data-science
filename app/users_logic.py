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