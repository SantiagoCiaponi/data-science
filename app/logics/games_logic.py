import pandas as pd
import config
from fastapi import HTTPException
from ..models import Game, Item

def build_game_from_row(row: pd.Series) -> Game:
    return Game(
        id=int(row[config.GAME_ID_COLUMN]),
        title=row[config.GAME_TITLE_COLUMN],
        description=row.get(config.GAME_DESCRIPTION_COLUMN, ""),
        platforms=row.get(config.GAME_PLATFORMS_COLUMN, ""),
        metascore=float(row.get(config.GAME_METASCORE_COLUMN, 0)),
        userscore=float(row.get(config.GAME_USERSCORE_COLUMN, 0)),
        action_rpg=int(row.get(config.ACTION_RPG_COLUMN, 0)),
        fps=int(row.get(config.FPS_COLUMN, 0)),
        linear_action_adventure=int(row.get(config.LINEAR_ACTION_ADVENTURE_COLUMN, 0)),
        open_world_action=int(row.get(config.OPEN_WORLD_ACTION_COLUMN, 0)),
        survival=int(row.get(config.SURVIVAL_COLUMN, 0)),
    )

def get_game_genres(row: pd.Series) -> list[str]:
    genres = []
    for column in config.GAME_TO_USER_ATTRIBUTE_MAP:
        if int(row.get(column, 0)) == 1:
            genres.append(column)
    return genres

def build_item_from_row(row: pd.Series) -> Item:
    return Item(
        id=int(row[config.GAME_ID_COLUMN]),
        name=row[config.GAME_TITLE_COLUMN],
        genre=", ".join(get_game_genres(row)),
    )

def get_game_feature_vector(row: pd.Series) -> list[float]:
    return [float(row.get(column, 0)) for column in config.GAME_TO_USER_ATTRIBUTE_MAP]

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
    return build_game_from_row(row)

def get_all_games() -> list[Game]:
    df = read_games_df()
    return [build_game_from_row(row) for _, row in df.iterrows()]
