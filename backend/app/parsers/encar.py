import asyncio
import httpx
import random
from app.schemas.car import CarCreate
from app.utils.currency import krw_to_usd
from app.utils.http import get_http_client

SEMAPHORE_LIMIT = 5
PHOTO_BASE_URL = "https://ci.encar.com"

SEARCH_API = (
    "https://api.encar.com/search/car/list/general"
    "?count=true"
    "&q=(And.Hidden.N._.CarType.Y.)"
    "&sr=%7CModifiedDate%7C{offset}%7C{limit}"
)

MANUFACTURER_MAP: dict[str, str] = {
    "기아": "Kia",
    "현대": "Hyundai",
    "쉐보레(GM대우)": "Chevrolet",
    "르노코리아": "Renault Korea",
    "KG모빌리티": "KG Mobility",
    "제네시스": "Genesis",
    "BMW": "BMW",
    "벤츠": "Mercedes-Benz",
    "아우디": "Audi",
    "폭스바겐": "Volkswagen",
    "볼보": "Volvo",
    "토요타": "Toyota",
    "렉서스": "Lexus",
}

MAX_RETRIES = 5
BASE_DELAY = 2
MAX_DELAY = 30

def get_english_manufacturer(korean_name: str) -> str:
    return MANUFACTURER_MAP.get(korean_name, korean_name)


def extract_photo_url(photos: list[dict]) -> str:
    if not photos:
        return ""
  
    sorted_photos = sorted(photos, key=lambda p: p.get("ordering", 999))
    return f"{PHOTO_BASE_URL}{sorted_photos[0].get('location', '')}"


def parse_search_result(item: dict) -> CarCreate | None:
   
    try:
      
        year_raw = str(item.get("Year") or "0")
        year = int(year_raw[:4]) if len(year_raw) >= 4 else 0

        price_krw = item["Price"] * 10_000
        price_usd = krw_to_usd(price_krw)

        return CarCreate(
            brand=get_english_manufacturer(item["Manufacturer"]),
            model=item["Model"], 
            year=year,
            mileage=float(item["Mileage"]),
            price=price_usd,
            image_url=extract_photo_url(item.get("Photos", [])),
            source_id=item["Id"],
        )
    
    except (KeyError, ValueError, TypeError) as e:
        print(f"Error for Id={item.get('Id')}: {e}")
        return None


def _retry_delay(attempt: int, response: httpx.Response | None = None) -> float:
    if response is not None:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return min(float(retry_after), MAX_DELAY)
            except ValueError:
                pass

    delay = min(BASE_DELAY * (2 ** attempt), MAX_DELAY)
    return delay * (0.5 + random.random())


async def fetch_page(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    offset: int,
    limit: int = 20,
) -> list[dict]:
    url = SEARCH_API.format(offset=offset, limit=limit)

    for attempt in range(MAX_RETRIES + 1):
        delay: float | None = None

        async with semaphore:
            try:
                response = await client.get(url)

                if response.status_code == 429 or response.status_code >= 500:
                    if attempt == MAX_RETRIES:
                        print(f"offset={offset}: {response.status_code} after {MAX_RETRIES} retries")
                        return []
                    delay = _retry_delay(attempt, response)
                else:
                    response.raise_for_status()
                    return response.json().get("SearchResults", [])

            except httpx.HTTPStatusError as e:
                print(f"offset={offset}: {e.response.status_code}")
                return []

            except (httpx.TransportError, ValueError) as e:
                if attempt == MAX_RETRIES:
                    print(f"offset={offset}: {e!r}")
                    return []
                delay = _retry_delay(attempt)

        if delay is not None:
            await asyncio.sleep(delay)

    return []

async def run_parser(total: int) -> list[CarCreate]:
    
    semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)
    page_size = 20  

    offsets = range(0, total, page_size)

    async with get_http_client() as client:
        tasks = [
            fetch_page(client, semaphore, offset, page_size)
            for offset in offsets
        ]
        pages = await asyncio.gather(*tasks, return_exceptions=True)

    all_items = []
    for page in pages:

        if isinstance(page, BaseException):
            continue

        for item in page:
            all_items.append(item)

    cars = []
    for item in all_items:
        car = parse_search_result(item)
        cars.append(car)

    valid_cars = []
    for car in cars:
        if car is not None:
            valid_cars.append(car)

    unique_cars_dict = {}
    for car in valid_cars:
        unique_cars_dict[car.source_id] = car 
            
    unique_cars = list(unique_cars_dict.values())
    
    print(f"Parsed cars: {len(valid_cars)} of {len(all_items)} ads")
    return unique_cars