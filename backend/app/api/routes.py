from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.schemas.car import CarOut
from app.services.car_service import CarService

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.get("/cars", response_model=list[CarOut])
async def get_cars(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0),
    limit: int = Query(20)
    ):
    service = CarService(db)
    return await service.get_cars(skip=skip, limit=limit)

@router.post("/cars/refresh", response_model=dict)
async def refresh_cars(db: AsyncSession = Depends(get_db)):
    service = CarService(db)
    await service.refresh_cars()
    return {"Called car parser"}