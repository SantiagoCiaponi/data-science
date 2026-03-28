from typing import Dict, List
import config
from pydantic import BaseModel, Field, create_model

UserAttributes = create_model(
    "UserAttributes",
    **{
        column: (float, Field(default=0.0))
        for column in config.get_user_attribute_columns()
    },
)

class Item(BaseModel):
    id: int
    name: str
    genre: str
    description: str
    userscore: float

class ItemArray(BaseModel):
    items: List[Item]

class Error(BaseModel):
    code: str
    message: str

class User(BaseModel):
    id: int
    username: str
    attributes: UserAttributes

class UserCreationDTO(BaseModel):
    username: str
    attributes: UserAttributes = Field(default_factory=UserAttributes)

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
    updatedAttributes: UserAttributes
