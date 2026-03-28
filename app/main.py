from fastapi import FastAPI, Query
from .models import (Game, GameArray, ItemArray, PreferenceCreateDTO, PreferenceCreatedResponse, User, UserCreationDTO)
from .logics.games_logic import get_all_games, get_game
from .logics.preferences_logic import create_preference
from .logics.recommendations_logic import get_k_recommendations
from .logics.users_logic import create_user, get_csv_user

app = FastAPI(title="Sistema Recomendador - Ciencia de Datos 2025", docs_url="/")

@app.post("/user", response_model=User, tags=["CRUD: Usuario"])
async def create_user_endpoint(payload: UserCreationDTO):
    return create_user(payload)

@app.get("/user/{userId}", response_model=User, tags=["CRUD: Usuario"])
async def get_user(userId: int):
    return get_csv_user(userId)

@app.get("/game", response_model=GameArray, tags=["CRUD: Juegos"])
async def get_games():
    return GameArray(games=get_all_games())

@app.get("/game/{gameId}", response_model=Game, tags=["CRUD: Juegos"])
async def get_game_by_id(gameId: int):
    return get_game(gameId)

@app.get("/user/{userId}/recommend", response_model=ItemArray, tags=["Sistema Recomendador"])
async def get_recommendations(userId: int, n: int = Query(5)):
    user = get_csv_user(userId)
    items = get_k_recommendations(user.id, n)
    return ItemArray(items=items)

@app.post("/user/{userId}/preference/{itemId}", response_model=PreferenceCreatedResponse, tags=["Sistema Recomendador"])
async def add_preference(userId: int, itemId: int, ranking: int):
    payload = PreferenceCreateDTO(user_id=userId, item_id=itemId, ranking=ranking)
    return create_preference(payload)