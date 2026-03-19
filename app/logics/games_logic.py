import pandas as pd
import config
from fastapi import HTTPException
from ..models import Game

def read_games_df() -> pd.DataFrame:
    return pd.read_csv(config.GAMES_CSV)

def get_game_row(game_id: int) -> pd.Series:
    df = read_games_df()
    game_row = df[df[config.GAME_ID_COLUMN] == game_id]

    if game_row.empty:
        raise HTTPException(status_code=404, detail=f"Juego {game_id} no encontrado")

    return game_row.iloc[0]

def get_game(game_id: int) -> Game:
    row = get_game_row(game_id)
    return Game(
        id=int(row[config.GAME_ID_COLUMN]),
        title=row[config.GAME_TITLE_COLUMN],
        description=row.get(config.GAME_DESCRIPTION_COLUMN, ""),
        platforms=row.get(config.GAME_PLATFORMS_COLUMN, ""),
    )

def get_all_games() -> list[Game]:
    df = read_games_df()
    return [
        Game(
            id=int(row[config.GAME_ID_COLUMN]),
            title=row[config.GAME_TITLE_COLUMN],
            description=row.get(config.GAME_DESCRIPTION_COLUMN, ""),
            platforms=row.get(config.GAME_PLATFORMS_COLUMN, ""),
        )
        for _, row in df.iterrows()
    ]
