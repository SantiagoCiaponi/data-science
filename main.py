import pandas as pd
import os
from fastapi import FastAPI, HTTPException, Query
from models import User, ItemArray, Error
import recommendation

app = FastAPI(title="sistema recomendador - Ciencia de Datos 2025")
CSV_FILE = "usuarios.csv"
PREF_CSV = "preferencias.csv"

# inicializar base de datos (CSV)
def init_db():
    if not os.path.exists(CSV_FILE):
        # creamos CSV con columnas basicas (basadas en el modelo User)
        df = pd.DataFrame(columns=["id", "username", "field1", "field2"])
        # 'to_csv' por dios esto en C++ son como 500 lineas
        df.to_csv(CSV_FILE, index=False)

    if not os.path.exists(PREF_CSV):
        # relacionamos userId con itemId
        df_prefs = pd.DataFrame(columns=["userId", "itemId"])
        df_prefs.to_csv(PREF_CSV, index=False)

# cuando arranca:
@app.on_event("startup")
async def startup_event():
    init_db()

# --- endpoints ---

# cargar un nuevo usuario
@app.post("/user", response_model=User, tags=["sistema recomendador"])
async def create_user(user: User):
    """Insertar un nuevo usuario a la base de datos CSV"""
    df = pd.read_csv(CSV_FILE)
    
    # si ya existe lo boleteamos 
    if user.id in df["id"].values:
        raise HTTPException(status_code=400, detail="El ID de usuario ya existe")
    
    # creamos un row con datos del usuario. Que lindo los lenguajes no tipados
    # (para programar estas cosas, no para produccion jajajajajjaa)
    new_user_row = {
        "id": user.id,
        "username": user.username,
        "field1": user.attributes.get("field1", ""),
        "field2": user.attributes.get("field2", "")
    }
    
    df = pd.concat([df, pd.DataFrame([new_user_row])], ignore_index=True)
    # agregamos al csv
    df.to_csv(CSV_FILE, index=False)
    # devolvemos usuario
    return user

# obtener un usuario
@app.get("/user/{userId}", response_model=User, tags=["sistema recomendador"])
async def get_user(userId: int):
    """obtener los datos del usuario desde el CSV"""
    # leemos el csv
    df = pd.read_csv(CSV_FILE)
    # buscamos el usuario por id
    user_row = df[df["id"] == userId]
    
    # si no está (user_row vuelve empty)
    if user_row.empty:
        raise HTTPException(status_code=404, detail="usuario no encontrado fiera segui intentando")
    
    # iloc obtiene la primer fila (debería ser la unica) y la convertimos a tipo User
    row = user_row.iloc[0]
    return User(
        id=int(row["id"]),
        username=row["username"],
        attributes={"field1": str(row["field1"]), "field2": str(row["field2"])}
    )

# obtener la recomendacion de un usuario
@app.get("/user/{userId}/recommend", response_model=ItemArray, tags=["sistema recomendador"])
async def get_recommendations(userId: int, n: int = Query(..., alias="n")):
    """obtener n recomendaciones para un usuario determinado"""
    df = pd.read_csv(CSV_FILE)
    
    if userId not in df["id"].values:
        raise HTTPException(status_code=404, detail="User not found")
    
    # llamada al motor de recomendaciones. harcodeado de momento...
    return {"items": []}

# registrar una preferencia (compra o like)
@app.post("/user/{userId}/preference/{itemId}", tags=["sistema recomendador"])
async def add_preference(userId: int, itemId: int):
    """Registrar que un usuario compró/le gustó un item"""
    df_u = pd.read_csv(CSV_FILE)
    if userId not in df_u["id"].values:
        raise HTTPException(status_code=404, detail="Usuario inexistente")
    
    df_p = pd.read_csv(PREF_CSV)
    new_pref = {"userId": userId, "itemId": itemId}
    df_p = pd.concat([df_p, pd.DataFrame([new_pref])], ignore_index=True)
    df_p.to_csv(PREF_CSV, index=False)
    
    return {"message": "Preferencia registrada", "userId": userId, "itemId": itemId}