from pydantic import BaseModel 

class UploadImage(BaseModel):
    image_base64: str = ""
    image_url: str = ""

class Words(BaseModel):
    words: list[str] = []