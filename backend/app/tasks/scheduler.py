from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.db.session import AsyncSessionLocal
from app.services.car_service import CarService
import logging

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def scheduled_parse() -> None:
    async with AsyncSessionLocal() as session:
        service = CarService(session)
        try:
            await service.refresh_cars()
            
        except Exception as e:
            logger.error(f"Scheduled parse failed: {e}")


def start_scheduler() -> None:
    scheduler.add_job(
        scheduled_parse,
        trigger=CronTrigger(hour=3, minute=0),
        id="daily_parse",
        replace_existing=True,
    )
    scheduler.start()


def shutdown_scheduler() -> None:
    scheduler.shutdown(wait=False)