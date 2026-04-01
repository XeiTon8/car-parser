from pydantic import BaseModel, ConfigDict

class CarBase(BaseModel):
    brand: str
    model: str
    year: int
    mileage: float
    price: float
    image_url: str

class CarOut(CarBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class CarCreate(CarBase):
    source_id: str | None = None