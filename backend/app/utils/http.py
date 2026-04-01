import httpx

def get_http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json",
            "Accept-Language": "ko-KR,ko;q=0.9",
        },
        follow_redirects=True,
    )