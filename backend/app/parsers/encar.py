import asyncio
import httpx
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


async def fetch_page(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    offset: int,
    limit: int = 20,
) -> list[dict]:
    url = SEARCH_API.format(offset=offset, limit=limit)
    
    async with semaphore:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get("SearchResults", [])
        
        except httpx.HTTPError as e:
            print(f"Error fetching offset={offset}: {e}")
            return []


async def run_parser(total: int = 100) -> list[CarCreate]:
    
    semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)
    page_size = 20  

    offsets = range(0, total, page_size)

    async with get_http_client() as client:
        tasks = [
            fetch_page(client, semaphore, offset, page_size)
            for offset in offsets
        ]
        pages = await asyncio.gather(*tasks)

    all_items = []
    for page in pages:
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