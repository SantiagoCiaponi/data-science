from fastapi import HTTPException

class UserNotFoundException(HTTPException):
    def __init__(self, user_id: int):
        super().__init__(status_code=404, detail=f"Usuario {user_id} no encontrado")

class GameNotFoundException(HTTPException):
    def __init__(self, game_id: int):
        super().__init__(status_code=404, detail=f"Juego {game_id} no encontrado")
