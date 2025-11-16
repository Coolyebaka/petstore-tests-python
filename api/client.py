from typing import Any, Dict, Optional, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.settings import Settings
from utils.logger import logger


class APIClient:
    def __init__(self, base_path: str = ""):
        self.base_url = Settings.get_base_url()
        self.base_path = base_path.rstrip("/")
        self.session = requests.Session()

        retry_strategy = Retry(
            total=Settings.MAX_RETRIES,
            backoff_factor=Settings.RETRY_DELAY,
            status_forcelist=[429, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        )

        retry_strategy_with_404 = Retry(
            total=Settings.MAX_RETRIES,
            backoff_factor=Settings.RETRY_DELAY,
            status_forcelist=[404, 429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self.adapter_with_404 = HTTPAdapter(max_retries=retry_strategy_with_404)

        self.session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )

    def _build_url(self, endpoint: str) -> str:
        endpoint = endpoint.lstrip("/")

        if self.base_path:
            full_path = f"{self.base_path}/{endpoint}"
        else:
            full_path = f"/{endpoint}" if endpoint else ""

        return f"{self.base_url}{full_path}"

    def _log_request(self, method: str, url: str, **kwargs) -> None:
        if Settings.LOG_REQUESTS:
            logger.info(f"Request: {method} {url}")
            if "json" in kwargs:
                logger.debug(f"Request body: {kwargs['json']}")
            if "params" in kwargs:
                logger.debug(f"Request params: {kwargs['params']}")
            if "data" in kwargs:
                logger.debug(f"Request data: {kwargs['data']}")

    def _log_response(self, response: requests.Response) -> None:
        if Settings.LOG_RESPONSES:
            logger.info(f"Response: {response.status_code} {response.reason}")
            try:
                if response.headers.get("content-type", "").startswith(
                    "application/json"
                ):
                    logger.debug(f"Response body: {response.json()}")
            except Exception:
                logger.debug(f"Response body: {response.text[:200]}")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        expected_status: Optional[int] = None,
        retry_on_404: bool = False,
    ) -> requests.Response:
        url = self._build_url(endpoint)

        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)

        self._log_request(
            method, url, params=params, json=json_data, data=data, files=files
        )

        try:
            if retry_on_404:
                temp_session = requests.Session()
                temp_session.headers.update(request_headers)
                temp_session.mount("http://", self.adapter_with_404)
                temp_session.mount("https://", self.adapter_with_404)

                response = temp_session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    data=data,
                    files=files,
                    headers=request_headers,
                    timeout=Settings.get_timeout(),
                )
                temp_session.close()
            else:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    data=data,
                    files=files,
                    headers=request_headers,
                    timeout=Settings.get_timeout(),
                )

            self._log_response(response)

            if expected_status is not None:
                assert response.status_code == expected_status, (
                    f"Expected status {expected_status}, got {response.status_code}. "
                    f"Response: {response.text}"
                )

            return response

        except requests.RequestException as e:
            logger.error(f"Request failed: {method} {url} - {str(e)}")
            raise

    def get(
        self,
        endpoint: str = "",
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        expected_status: Optional[int] = None,
        retry_on_404: bool = False,
    ) -> requests.Response:
        return self._make_request(
            "GET",
            endpoint,
            params=params,
            headers=headers,
            expected_status=expected_status,
            retry_on_404=retry_on_404,
        )

    def post(
        self,
        endpoint: str = "",
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str]] = None,
        files: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        expected_status: Optional[int] = None,
        retry_on_404: bool = False,
    ) -> requests.Response:
        return self._make_request(
            "POST",
            endpoint,
            json_data=json_data,
            data=data,
            files=files,
            params=params,
            headers=headers,
            expected_status=expected_status,
            retry_on_404=retry_on_404,
        )

    def put(
        self,
        endpoint: str = "",
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str]] = None,
        headers: Optional[Dict[str, str]] = None,
        expected_status: Optional[int] = None,
        retry_on_404: bool = False,
    ) -> requests.Response:
        return self._make_request(
            "PUT",
            endpoint,
            json_data=json_data,
            data=data,
            headers=headers,
            expected_status=expected_status,
            retry_on_404=retry_on_404,
        )

    def patch(
        self,
        endpoint: str = "",
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str]] = None,
        headers: Optional[Dict[str, str]] = None,
        expected_status: Optional[int] = None,
        retry_on_404: bool = False,
    ) -> requests.Response:
        return self._make_request(
            "PATCH",
            endpoint,
            json_data=json_data,
            data=data,
            headers=headers,
            expected_status=expected_status,
            retry_on_404=retry_on_404,
        )

    def delete(
        self,
        endpoint: str = "",
        headers: Optional[Dict[str, str]] = None,
        expected_status: Optional[int] = None,
        retry_on_404: bool = False,
    ) -> requests.Response:
        return self._make_request(
            "DELETE",
            endpoint,
            headers=headers,
            expected_status=expected_status,
            retry_on_404=retry_on_404,
        )

    def close(self) -> None:
        self.session.close()
