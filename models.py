from pydantic import BaseModel
from typing import Dict, List, Optional

class Item(BaseModel):
    id: int
    name: str
    genre: str

class ItemArray(BaseModel):
    items: List[Item]

class Error(BaseModel):
    code: str
    message: str

class UserAttributes(BaseModel):
    open_world_action_preference: float
    fps_preference: float
    survival_preference: float
    action_rpg_preference: float
    linear_action_adventure_preference: float

class User(BaseModel):
    id: int
    username: str
    attributes: UserAttributes

class UserCreationDTO(BaseModel):
    username: str
    attributes: UserAttributes