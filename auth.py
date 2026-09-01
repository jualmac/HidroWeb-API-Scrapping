import os
import time
import json
import logging
import pandas as pd
from dotenv import load_dotenv
import requests
from util import BASE_URL, configure_logging

logger = configure_logging(__name__)

load_dotenv()

ID=os.getenv("ID")
PASS=os.getenv("PASS")

# ANA returns 503/504 when the service is down; wait then give up instead of hammering;
OUTAGE_STATUS_CODES = {503, 504}
OUTAGE_SLEEP_MINUTES = 10
OUTAGE_MAX_FAILURES = 3


def request_with_outage_guard(method: str, url: str, **request_kwargs) -> requests.Response:
    """
    Perform an HTTP request. On 503/504, sleep and retry; abort the process after a few failures;
    """
    failures = 0
    while True:
        response = requests.request(method, url, **request_kwargs)
        if response.status_code not in OUTAGE_STATUS_CODES:
            return response

        failures += 1
        if failures >= OUTAGE_MAX_FAILURES:
            logger.error(
                "API outage (%s). Aborting after %s consecutive 503/504 responses.",
                response.status_code,
                OUTAGE_MAX_FAILURES,
            )
            raise SystemExit(1)

        logger.warning(
            "API outage (%s). Failure %s/%s. Sleeping %s min.",
            response.status_code,
            failures,
            OUTAGE_MAX_FAILURES,
            OUTAGE_SLEEP_MINUTES,
        )
        time.sleep(OUTAGE_SLEEP_MINUTES * 60)


def get_auth() -> str:
    '''
    Gets the proper token necessary for the other API's from the HidroWeb service
    '''
    # Define URL;
    url = BASE_URL + "OAUth/v1"

    headers = {
        'accept': '*/*',
        'Identificador': ID,
        'Senha': PASS
    }

    # Create request;
    logger.info("Attempting connection...")
    response = request_with_outage_guard("GET", url, headers=headers, timeout=60)

    # Request Reponse:
    if response.status_code == 200:
        data = response.json()
        logger.info("Credentials acquired: %s", data)
        return(data['items']['tokenautenticacao'])
    else:
        logger.error("Request failed with status code %s", response.status_code)
        return 0