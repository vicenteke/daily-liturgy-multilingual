import httpx


def fetch_cancaonova_page(url: str) -> str:
    response = httpx.get(url, timeout=20, follow_redirects=True)
    response.raise_for_status()
    return response.text
