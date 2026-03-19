from typing import List

from pydantic import BaseModel


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

class Game(BaseModel):
    id: int
    title: str
    description: str
    platforms: str


class GameArray(BaseModel):
    games: List[Game]

class PreferenceCreateDTO(BaseModel):
    user_id: int
    item_id: int
    ranking: int

class Preference(BaseModel):
    userId: int
    itemId: int
    ranking: int

class PreferenceCreatedResponse(BaseModel):
    message: str
    userId: int
    itemId: int
    ranking: int
    updatedAttributes: UserAttributes
