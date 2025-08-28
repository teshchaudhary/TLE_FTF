from pydantic import BaseModel

class Disaster(BaseModel):
    id: str
    description: str
    severity: str
    location: dict

class Alert(BaseModel):
    type: str
    message: str
