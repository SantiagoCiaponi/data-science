### Parámetros para la lógica de recomendaciones
RECOMMENDATION_CONTENT_WEIGHT = 0.8
RECOMMENDATION_SERENDIPITY_WEIGHT = 0.2
SERENDIPITY_TARGET_CONTENT_SCORE = 0.2
SERENDIPITY_ALLOWED_DEVIATION = 0.2
SERENDIPITY_QUALITY_WEIGHT = 0.1

COLLABORATIVE_RANKING_MAP = {
    1: -1.0,
    2: -0.5,
    3: 0.0,
    4: 0.5,
    5: 1.0,
}

PREFERENCE_MIN_VALUE = 0.0
PREFERENCE_MAX_VALUE = 10.0
PREFERENCE_UPDATE_ALPHA = 1.0

RANKING_WEIGHT_MAP = {
    1: -1.0,
    2: -0.5,
    3: 0.0,
    4: 0.75,
    5: 1.0,
}

# Paths
USERS_CSV = "database/usuarios.csv"
PREFERENCES_CSV = "database/preferencias.csv"
GAMES_CSV = "database/juegos.csv"

### Columnas de los CSV
# User
USER_ID_COLUMN = "id"
USERNAME_COLUMN = "username"

# Juego
GAME_ID_COLUMN = "id"
GAME_TITLE_COLUMN = "title"
GAME_DESCRIPTION_COLUMN = "description"
GAME_PLATFORMS_COLUMN = "platforms"
GAME_METASCORE_COLUMN = "metascore"
GAME_USERSCORE_COLUMN = "userscore"

# Preferencias
PREFERENCE_USER_ID_COLUMN = "userId"
PREFERENCE_ITEM_ID_COLUMN = "itemId"
PREFERENCE_RANKING_COLUMN = "ranking"

# Géneros fijos de la base
ACTION_GENRE = "Action"
ADVENTURE_GENRE = "Adventure"
PLATFORMER_GENRE = "Platformer"
PUZZLE_HORROR_GENRE = "Puzzle/Horror"
RPG_GENRE = "RPG"
RACING_GENRE = "Racing"
SHOOTER_GENRE = "Shooter"
SIMULATION_GENRE = "Simulation"
SPORTS_GENRE = "Sports"
STRATEGY_GENRE = "Strategy"

DETECTED_GENRES = [
    ACTION_GENRE,
    ADVENTURE_GENRE,
    PLATFORMER_GENRE,
    PUZZLE_HORROR_GENRE,
    RPG_GENRE,
    RACING_GENRE,
    SHOOTER_GENRE,
    SIMULATION_GENRE,
    SPORTS_GENRE,
    STRATEGY_GENRE,
]

GENRE_COLUMN_MAP = {
    ACTION_GENRE: "action",
    ADVENTURE_GENRE: "adventure",
    PLATFORMER_GENRE: "platformer",
    PUZZLE_HORROR_GENRE: "puzzle_horror",
    RPG_GENRE: "rpg",
    RACING_GENRE: "racing",
    SHOOTER_GENRE: "shooter",
    SIMULATION_GENRE: "simulation",
    SPORTS_GENRE: "sports",
    STRATEGY_GENRE: "strategy",
}

GAME_GENRE_COLUMNS = [(genre_name, GENRE_COLUMN_MAP[genre_name]) for genre_name in DETECTED_GENRES]

ACTION_PREFERENCE = "action_preference"
ADVENTURE_PREFERENCE = "adventure_preference"
PLATFORMER_PREFERENCE = "platformer_preference"
PUZZLE_HORROR_PREFERENCE = "puzzle_horror_preference"
RPG_PREFERENCE = "rpg_preference"
RACING_PREFERENCE = "racing_preference"
SHOOTER_PREFERENCE = "shooter_preference"
SIMULATION_PREFERENCE = "simulation_preference"
SPORTS_PREFERENCE = "sports_preference"
STRATEGY_PREFERENCE = "strategy_preference"

GAME_TO_USER_ATTRIBUTE_MAP = {
    ACTION_GENRE: ACTION_PREFERENCE,
    ADVENTURE_GENRE: ADVENTURE_PREFERENCE,
    PLATFORMER_GENRE: PLATFORMER_PREFERENCE,
    PUZZLE_HORROR_GENRE: PUZZLE_HORROR_PREFERENCE,
    RPG_GENRE: RPG_PREFERENCE,
    RACING_GENRE: RACING_PREFERENCE,
    SHOOTER_GENRE: SHOOTER_PREFERENCE,
    SIMULATION_GENRE: SIMULATION_PREFERENCE,
    SPORTS_GENRE: SPORTS_PREFERENCE,
    STRATEGY_GENRE: STRATEGY_PREFERENCE,
}

USER_ATTRIBUTE_COLUMNS = [
    ACTION_PREFERENCE,
    ADVENTURE_PREFERENCE,
    PLATFORMER_PREFERENCE,
    PUZZLE_HORROR_PREFERENCE,
    RPG_PREFERENCE,
    RACING_PREFERENCE,
    SHOOTER_PREFERENCE,
    SIMULATION_PREFERENCE,
    SPORTS_PREFERENCE,
    STRATEGY_PREFERENCE,
]

USER_COLUMNS = [
    USER_ID_COLUMN,
    USERNAME_COLUMN,
    *USER_ATTRIBUTE_COLUMNS,
]

def get_game_to_user_attribute_map() -> dict[str, str]:
    return GAME_TO_USER_ATTRIBUTE_MAP

def get_game_genre_columns() -> list[tuple[str, str]]:
    return GAME_GENRE_COLUMNS

def get_genre_column_name(genre_name: str) -> str:
    return GENRE_COLUMN_MAP[genre_name]

def get_user_attribute_columns() -> list[str]:
    return USER_ATTRIBUTE_COLUMNS

def get_user_columns() -> list[str]:
    return USER_COLUMNS
