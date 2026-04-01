from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.car_repo import CarRepository
from app.parsers.encar import run_parser
from app.models.car import Car


class CarService:
    def __init__(self, session: AsyncSession):
        self.repo = CarRepository(session)

    async def get_cars(self, skip: int = 0, limit: int = 20) -> list[Car]:
        return await self.repo.get_all(skip=skip, limit=limit)

    async def refresh_cars(self) -> int:
        cars = await run_parser(total=50)
        return await self.repo.upsert_many(cars)