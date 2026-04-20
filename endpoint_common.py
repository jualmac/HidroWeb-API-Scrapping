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

from api_auth import get_auth
from db_handler import DBConnection

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

class Hidroweb_API():
    def __init__(self) -> None:
        self.token = get_auth()

    def collect_simple_endpoint_data(
        *,
        self,
        logger,
        url: str,
        table_name: str,
        inplace: bool,
        params: dict[str, Any] | None = None,
    ) -> None:
        """
        Collect one-shot endpoint data and persist response items into DuckDB database;
        """
        
        if not self.token:
            logger.error("Failed to get authentication token")
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        response, _ = request_with_auth_retry(
            url=url,
            headers=headers,
            params=params,
            get_auth_token=get_auth,
            request_logger=logger,
        )

        if response.status_code != 200:
            logger.error("Request failed with status code: %s", response.status_code)
            logger.error("Response text: %s", response.text)
            return

        payload = response.json()
        if "items" not in payload or not payload["items"]:
            logger.warning("No data items found in response for URL '%s'", url)
            return

        df = pd.DataFrame(payload["items"])
        db_handler = DBConnection()
        db_handler.write(df, table_name, inplace=inplace)
        logger.info("Data collected from '%s' and saved to '%s'", url, table_name)

    def HidrosatSerieDados():
        pass
    def HidrosatInventarioEstacoes():
        pass
    def HidroUF():
        pass
    def HidroSubBacia():
        pass
    def HidroSerieVazao():
        pass
    def HidroSerieSedimentos():
        pass
    def HidroSerieResumoDescarga():
        pass
    def HidroSerieQA():
        pass
    def HidroSeriePerfilTransversal():
        pass
    def HidroSerieGranulometria():
        pass
    def HidroSerieCurvaDescarga():
        pass
    def HidroSerieCotas():
        pass
    def HidroSerieChuva():
        pass
    def HidroRio():
        pass
    def HidroMunicipio():
        pass
    def HidroInventarioEstacoes():
        pass
    def HidroEntidade():
        pass
    def HidroBacia():
        pass

########################################################################################################################
# # Needs to be separated;
# def HidroinfoanaSerieTelemetricaDetalhada_v1():
#     pass
# def HidroinfoanaSerieTelemetricaDetalhada_v2():
#     pass
# def HidroinfoanaSerieTelemetricaAdotada_v1():
#     pass
# def HidroinfoanaSerieTelemetricaAdotada_v2():
#     pass


# def iter_hidroweb_date_chunks(
#     start_date: str | datetime, 
#     end_date: str | datetime
#     ) -> Iterator[dict]:
#     """
#     Split a date window into API-compatible chunks while respecting the 30-day hard limit.

#     The HidroWeb endpoints accept only specific range labels, so this helper always chooses
#     the largest valid chunk for the remaining window to minimize request count;
#     """
#     if isinstance(start_date, str):
#         start_dt = datetime.strptime(start_date, "%Y-%m-%d")
#     else:
#         start_dt = start_date

#     if isinstance(end_date, str):
#         end_dt = datetime.strptime(end_date, "%Y-%m-%d")
#     else:
#         end_dt = end_date

#     if start_dt > end_dt:
#         raise ValueError("start_date cannot be after end_date")

#     # Ordered from largest to smallest to always minimize number of requests;
#     chunk_options = [
#         ("DIAS_30", 30),
#         ("DIAS_21", 21),
#         ("DIAS_14", 14),
#         ("DIAS_7", 7),
#         ("DIAS_2", 2),
#     ]

#     current_date = start_dt
#     while current_date <= end_dt:
#         remaining_days = (end_dt - current_date).days + 1

#         if remaining_days == 1:
#             # API has no DIAS_1 option, so DIAS_2 must be used with one-day effective span;
#             range_days = "DIAS_2"
#             requested_chunk_days = 1
#         else:
#             range_days = "DIAS_2"
#             requested_chunk_days = 2
#             for label, days in chunk_options:
#                 if remaining_days >= days:
#                     range_days = label
#                     requested_chunk_days = days
#                     break

#         # The final chunk may be shorter than requested if we are at the end of the interval;
#         chunk_end_date = min(current_date + timedelta(days=requested_chunk_days - 1), end_dt)
#         actual_chunk_days = (chunk_end_date - current_date).days + 1

#         yield {
#             "start_date": current_date,
#             "end_date": chunk_end_date,
#             "range_days": range_days,
#             "actual_chunk_days": actual_chunk_days,
#         }

#         current_date = chunk_end_date + timedelta(days=1)


# def collect_chunked_endpoint_data(
#     *,
#     url: str,
#     station_code: str,
#     start_date: str,
#     end_date: str,
#     table_name: str,
#     inplace: bool,
#     logger,
#     date_filter_type: str = "DATA_LEITURA",
#     station_param_name: str = "Código da Estação",
#     date_filter_param_name: str = "Tipo Filtro Data",
#     search_date_param_name: str = "Data de Busca (yyyy-MM-dd)",
#     range_param_name: str = "Range Intervalo de busca",
#     extra_params: dict[str, Any] | None = None,
#     ) -> None:
#     """
#     Collect endpoint data in date chunks while respecting API max-range limits;
#     """
#     token = get_auth()
#     if not token:
#         logger.error("Failed to get authentication token")
#         return

#     headers = {"accept": "*/*", "Authorization": f"Bearer {token}"}
#     all_dataframes: list[pd.DataFrame] = []
#     chunk_number = 1

#     # Chunks are generated to guarantee each call stays under API date limits;
#     for chunk in iter_hidroweb_date_chunks(start_date, end_date):
#         search_date = chunk["start_date"].strftime("%Y-%m-%d")
#         range_days = chunk["range_days"]
#         actual_chunk_days = chunk["actual_chunk_days"]

#         params: dict[str, Any] = {
#             station_param_name: station_code,
#             date_filter_param_name: date_filter_type,
#             search_date_param_name: search_date,
#             range_param_name: range_days,
#         }
#         if extra_params:
#             params.update(extra_params)

#         logger.info(
#             "Chunk %s: %s | range %s | days %s",
#             chunk_number,
#             search_date,
#             range_days,
#             actual_chunk_days,
#         )
#         response, headers = request_with_auth_retry(
#             url=url,
#             headers=headers,
#             params=params,
#             get_auth_token=get_auth,
#             request_logger=logger,
#         )

#         if response.status_code != 200:
#             logger.error("Chunk %s failed with status code: %s", chunk_number, response.status_code)
#             logger.error("Response text: %s", response.text)
#             chunk_number += 1
#             continue

#         payload = response.json()
#         if "items" in payload and payload["items"]:
#             all_dataframes.append(pd.DataFrame(payload["items"]))
#             logger.info("Chunk %s collected successfully", chunk_number)
#         else:
#             logger.info("Chunk %s returned no items", chunk_number)
#         chunk_number += 1

#     if not all_dataframes:
#         logger.warning("No data collected for endpoint '%s'", url)
#         return

#     combined_df = pd.concat(all_dataframes, ignore_index=True)
#     db_handler = DBConnection()
#     db_handler.write(combined_df, table_name, inplace=inplace)
#     logger.info("Collected %s records and saved to '%s'", len(combined_df), table_name)
