from pydantic import BaseModel, Field
from datetime import datetime


class WalkOrderCreate(BaseModel):
    apartment_number: int = Field(..., gt=0, description="Номер квартиры")
    pet_name: str = Field(..., min_length=1, max_length=50, description="Кличка питомца")
    pet_breed: str = Field(..., min_length=1, max_length=50, description="Порода питомца")
    walk_time: datetime = Field(..., description="Время выгула")


class WalkOrder(BaseModel):
    id: int
    apartment_number: int
    pet_name: str
    pet_breed: str
    walk_time: datetime
    walker_name: str

    class Config:
        from_attributes = True
