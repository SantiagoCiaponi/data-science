from pydantic import BaseModel
from typing import Dict, List, Optional

class User(BaseModel):
    id: int
    username: str
    attributes: Dict[str, str]

class Item(BaseModel):
    id: int
    name: str
    attributes: Dict[str, str]

class ItemArray(BaseModel):
    items: List[Item]

class Error(BaseModel):
    code: str
    message: str