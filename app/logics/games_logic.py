import pandas as pd
import config
from ..exceptions import GameNotFoundException
from ..models import Game, Item

# Devuelve la lista de géneros activos de un juego
def get_game_genres(row: pd.Series) -> list[str]:
    return [
        genre_name
        for genre_name, column_name in config.get_game_genre_columns()
        if int(float(row.get(column_name, 0)) > 0) == 1
    ]

# Devuelve los flags one-hot del juego en formato diccionario
def get_game_genre_flags(row: pd.Series) -> dict[str, int]:
    return {
        column_name: int(float(row.get(column_name, 0)) > 0)
        for _, column_name in config.get_game_genre_columns()
    }

# Mapea una fila del DataFrame a un Game
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

# Mapea una fila del DataFrame a un Item
def build_item_from_row(row: pd.Series) -> Item:
    return Item(
        id=int(row[config.GAME_ID_COLUMN]),
        name=row[config.GAME_TITLE_COLUMN],
        genre=", ".join(get_game_genres(row)),
        description=row.get(config.GAME_DESCRIPTION_COLUMN, ""),
        userscore=float(row.get(config.GAME_USERSCORE_COLUMN, 0)),
    )

# Construye el vector de features del juego para recomendaciones
def get_game_feature_vector(row: pd.Series) -> list[float]:
    return [
        float(float(row.get(column_name, 0)) > 0)
        for _, column_name in config.get_game_genre_columns()
    ]

# Devuelve todos los juegos en formato DataFrame
def read_games_df() -> pd.DataFrame:
    return pd.read_csv(config.GAMES_CSV)

# Devuelve la fila de un juego a partir de su ID
def get_game_row(game_id: int) -> pd.Series:
    df = read_games_df()
    game_row = df[df[config.GAME_ID_COLUMN] == game_id]

    if game_row.empty:
        raise GameNotFoundException(game_id)

    return game_row.iloc[0]

def get_game(game_id: int) -> Game:
    row = get_game_row(game_id)
    return build_game_from_row(row)

def get_all_games() -> list[Game]:
    df = read_games_df()
    return [build_game_from_row(row) for _, row in df.iterrows()]
