from pydantic import BaseModel
from fastapi import Form

class Employee(BaseModel):
    employee_id: int
    firstname: str
    lastname: str
    time_met: str
    place_met: str
    picture: str
    role: str

    class Config:
        orm_mode = True