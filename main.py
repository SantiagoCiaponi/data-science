import pandas as pd
import os
from fastapi import FastAPI, HTTPException, Query
from models import User, ItemArray, Error, UserCreationDTO
from exceptions import UserNotFoundException
from recommendation import get_k_recommendations

app = FastAPI(title="Sistema Recomendador - Ciencia de Datos 2025")
CSV_FILE = "database/usuarios.csv"
PREF_CSV = "database/preferencias.csv"
GAMES_CSV = "database/games.csv"

def init_db():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=[
            "id",
            "username",
            "open_word_action_preference",
            "fps_preference",
            "survival_preference",
            "action_rpg_preference",
            "linear_action_adventure_preference",
        ])
        df.to_csv(CSV_FILE, index=False)

    if not os.path.exists(PREF_CSV):
        df_prefs = pd.DataFrame(columns=["userId", "itemId"])
        df_prefs.to_csv(PREF_CSV, index=False)

@app.on_event("startup")
async def startup_event():
    init_db()

# ---------- HELPERS ----------
def get_user_or_404(user_id: int) -> User:
    df = pd.read_csv(CSV_FILE)
    user_row = df[df["id"] == user_id]

    if user_row.empty:
        raise UserNotFoundException(user_id)

    row = user_row.iloc[0]
    return User(
        id=int(row["id"]),
        username=row["username"],
        attributes={
            "open_word_action_preference": float(row["open_word_action_preference"]),
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

# ----- ENDPOINTS -----
@app.post("/user", response_model=User, tags=["CRUD: Usuario"])
async def create_user(payload: UserCreationDTO):
    df = pd.read_csv(CSV_FILE)
    user_id = get_next_user_id()

    attrs = payload.attributes 

    new_user_row = {
        "id": user_id,
        "username": payload.username,
        "open_world_action_preference": attrs.open_world_action_preference,
        "fps_preference": attrs.fps_preference,
        "survival_preference": attrs.survival_preference,
        "action_rpg_preference": attrs.action_rpg_preference,
        "linear_action_adventure_preference": attrs.linear_action_adventure_preference,
    }

    df = pd.concat([df, pd.DataFrame([new_user_row])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

    return User(id=user_id, username=payload.username, attributes=payload.attributes)

@app.get("/user/{userId}", response_model=User, tags=["CRUD: Usuario"])
async def get_user(userId: int):
    return get_user_or_404(userId)

@app.get("/user/{userId}/recommend", response_model=ItemArray, tags=["Sistema Recomendador"])
async def get_recommendations(userId: int, k: int = Query(5)):
    user = get_user_or_404(userId)
    items = get_k_recommendations(user.id, k)
    return ItemArray(items=items)

@app.post("/user/{userId}/preference/{itemId}", tags=["Sistema Recomendador"])
async def add_preference(userId: int, itemId: int, ranking: int):
    user = get_user_or_404(userId)

    df_p = pd.read_csv(PREF_CSV)
    new_pref = {"userId": user.id, "itemId": itemId}
    df_p = pd.concat([df_p, pd.DataFrame([new_pref])], ignore_index=True)
    df_p.to_csv(PREF_CSV, index=False)

    return {"message": "Preferencia registrada", "userId": user.id, "itemId": itemId, "ranking": ranking}