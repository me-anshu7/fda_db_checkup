import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from typing import Optional


class HTTPXClient:
    def __init__(self):
        """Initialize the HTTPX client with HTTP/2 support"""
        # Essential headers for production
        self.headers = {
            "User-Agent": "FDA-DB-Checkup/1.0",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
        # Configure timeouts: 5s connect, 30s read
        self.timeout = httpx.Timeout(5.0, read=30.0)
        # Explicitly enable HTTP/2 support
        self.http2 = True

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
        # before_sleep=lambda retry_state: logger.warning(
        #     f"Retrying {retry_state.fn.__name__} due to {retry_state.outcome.exception()}"
        # )
    )
    async def async_get(self, url: str, params: Optional[dict] = None) -> dict:
        """Make an asynchronous GET request with HTTP/2."""
        async with httpx.AsyncClient(
            http2=self.http2, timeout=self.timeout, headers=self.headers
        ) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise HTTPError(f"HTTP error occurred: {e}") from e
            except httpx.RequestError as e:
                raise RequestError(f"Request error occurred: {e}") from e
            except ValueError as e:
                raise ValueError(f"Invalid JSON response: {e}") from e
