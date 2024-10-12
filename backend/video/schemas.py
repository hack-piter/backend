from pydantic import BaseModel


class ResponseMixin:
    status_code: int




class CameraCreate(BaseModel):
    threadURL: str

    class Config:
        orm_mode = True
        from_attributes = True


class VideoCreate(BaseModel):
    path: str
    state: str
    content_type: str
    content_length: int

    class Config:
        orm_mode = True
        from_attributes = True

class VideoUpdateState(BaseModel):
    state: str

    class Config:
        orm_mode = True
        from_attributes = True

