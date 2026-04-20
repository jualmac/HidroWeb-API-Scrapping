"""
Shared helpers for endpoint scripts;
"""
########################################################################################################################
#
# LIBRARIES
#
########################################################################################################################
import os
import logging
import requests
import numpy as np
import pandas as pd
from typing import Any
from datetime import datetime, timedelta
from typing import Callable, Iterator

from auth import get_auth
from db_handler import DBConnection
from util import START_DATE, END_DATE, BASE_URL, configure_logging

logger = configure_logging(__name__)

########################################################################################################################
#
# FUNCTIONS
#
########################################################################################################################
def request_with_auth_retry(
    *,
    url: str,
    get_auth_token: Callable[[], str],
    params: dict | None = None,
    headers: dict | None = None,
    method: str = "GET",
    max_auth_retries: int = 5,
    timeout: int = 60,
    request_logger: logging.Logger | None = None,
    ) -> tuple[requests.Response, dict]:
    """
    Perform an HTTP request and retry only authentication failures (401) with token refresh.
    """
    active_logger = request_logger or logger
    request_headers = dict(headers or {})
    auth_retries = 0

    while True:
        # A single execution path is used for all methods/endpoints to keep retry behavior consistent;
        response = requests.request(
            method=method.upper(),
            url=url,
            headers=request_headers,
            params=params,
            timeout=timeout,
        )

        if response.status_code != 401:
            return response, request_headers

        auth_retries += 1
        if auth_retries > max_auth_retries:
            active_logger.error(
                "Max authentication retries (%s) reached for URL %s", max_auth_retries, url
            )
            return response, request_headers

        active_logger.warning(
            "Authentication expired (401). Refreshing token (attempt %s/%s)",
            auth_retries,
            max_auth_retries,
        )
        refreshed_token = get_auth_token()
        if not refreshed_token:
            active_logger.error("Token refresh failed while retrying URL %s", url)
            return response, request_headers

        request_headers["Authorization"] = f"Bearer {refreshed_token}"