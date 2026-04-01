from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from app.models.car import Car
from app.schemas.car import CarCreate
from datetime import datetime, timezone


class CarRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, skip: int = 0, limit: int = 20) -> list[Car]:
        result = await self.session.execute(
            select(Car)
            .order_by(Car.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def upsert_many(self, cars: list[CarCreate]) -> int:
        if not cars:
            return 0

        now = datetime.now(timezone.utc)
        values = [
            {**car.model_dump(), "updated_at": now, "created_at": now}
            for car in cars
        ]

        stmt = insert(Car).values(values)
        stmt = stmt.on_conflict_do_update(
            index_elements=["source_id"],
            set_={
                "price": stmt.excluded.price,
                "mileage": stmt.excluded.mileage,
                "image_url": stmt.excluded.image_url,
                "updated_at": stmt.excluded.updated_at,
            }
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return len(cars)