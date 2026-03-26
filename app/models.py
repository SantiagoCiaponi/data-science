from typing import Dict, List
from pydantic import BaseModel, Field

class Item(BaseModel):
    id: int
    name: str
    genre: str

class ItemArray(BaseModel):
    items: List[Item]

class Error(BaseModel):
    code: str
    message: str

class User(BaseModel):
    id: int
    username: str
    attributes: Dict[str, float]

class UserCreationDTO(BaseModel):
    username: str
    attributes: Dict[str, float] = Field(default_factory=dict)

class Game(BaseModel):
    id: int
    title: str
    description: str
    platforms: str
    metascore: float
    userscore: float
    genres: List[str]
    genreFlags: Dict[str, int]

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
    updatedAttributes: Dict[str, float]
