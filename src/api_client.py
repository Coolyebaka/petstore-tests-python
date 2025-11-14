import os
import time
from typing import Any, Dict, Optional

import requests

DEFAULT_BASE_URL = "https://petstore.swagger.io/v2"


class ApiClient:
    """Простая обёртка над requests.Session.

    - хранит базовый URL;
    - даёт методы get/post/put/delete;
    - логирует запросы;
    - делает несколько попыток при сетевых ошибках.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: int = 20,
        retries: int = 3,
        retry_delay: float = 0.3,
    ) -> None:
        env_base = os.getenv("PETSTORE_BASE_URL") or DEFAULT_BASE_URL
        self.base_url = (base_url or env_base).rstrip("/")
        self.session = requests.Session()
        self.timeout = timeout
        self.retries = retries
        self.retry_delay = retry_delay

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def _log_request(
        self,
        method: str,
        url: str,
        kwargs: Dict[str, Any],
        resp: requests.Response,
    ) -> None:
        body_preview = resp.text[:200].replace("\n", " ")
        print(f"[API] {method} {url} -> {resp.status_code} {body_preview}")

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        url = self._url(path)

        last_exc: Optional[BaseException] = None
        for attempt in range(1, self.retries + 1):
            try:
                resp = self.session.request(
                    method=method,
                    url=url,
                    timeout=self.timeout,
                    **kwargs,
                )
                self._log_request(method, url, kwargs, resp)
                return resp
            except requests.RequestException as exc:
                last_exc = exc
                print(f"[API] attempt {attempt} failed: {exc}")
                if attempt < self.retries:
                    time.sleep(self.retry_delay)

        if last_exc:
            raise last_exc
        raise RuntimeError("Unexpected error")

    def get(self, path: str, **kwargs: Any) -> requests.Response:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> requests.Response:
        headers: Dict[str, str] = kwargs.pop("headers", {}) or {}
        headers.setdefault("Content-Type", "application/json")
        return self._request("POST", path, headers=headers, **kwargs)

    def put(self, path: str, **kwargs: Any) -> requests.Response:
        headers: Dict[str, str] = kwargs.pop("headers", {}) or {}
        headers.setdefault("Content-Type", "application/json")
        return self._request("PUT", path, headers=headers, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> requests.Response:
        return self._request("DELETE", path, **kwargs)
