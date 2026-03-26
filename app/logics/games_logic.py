import pandas as pd
import config
from fastapi import HTTPException
from ..models import Game, Item

def parse_game_genres(raw_genres: str) -> list[str]:
    if not raw_genres:
        return []
    return [genre.strip() for genre in str(raw_genres).split(",") if genre.strip()]

def get_game_genres(row: pd.Series) -> list[str]:
    return parse_game_genres(row.get(config.GAME_GENRES_COLUMN, ""))

def get_game_genre_flags(row: pd.Series) -> dict[str, int]:
    detected_genres = set(get_game_genres(row))
    return {
        config.normalize_genre_name(genre_name): int(genre_name in detected_genres)
        for genre_name in config.get_detected_genres()
    }

def build_game_from_row(row: pd.Series) -> Game:
    return Game(
        id=int(row[config.GAME_ID_COLUMN]),
        title=row[config.GAME_TITLE_COLUMN],
        description=row.get(config.GAME_DESCRIPTION_COLUMN, ""),
        platforms=row.get(config.GAME_PLATFORMS_COLUMN, ""),
        metascore=float(row.get(config.GAME_METASCORE_COLUMN, 0)),
        userscore=float(row.get(config.GAME_USERSCORE_COLUMN, 0)),
        genres=get_game_genres(row),
        genreFlags=get_game_genre_flags(row),
    )

def build_item_from_row(row: pd.Series) -> Item:
    return Item(
        id=int(row[config.GAME_ID_COLUMN]),
        name=row[config.GAME_TITLE_COLUMN],
        genre=", ".join(get_game_genres(row)),
    )

def get_game_feature_vector(row: pd.Series) -> list[float]:
    game_genres = set(get_game_genres(row))
    return [
        float(genre_name in game_genres)
        for genre_name in config.get_game_to_user_attribute_map()
    ]

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