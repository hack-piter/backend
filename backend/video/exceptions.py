from pydantic import BaseModel

class Exception(BaseModel):
    status: int
    message: str
