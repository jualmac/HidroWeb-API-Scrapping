"""
Shared helpers for endpoint scripts;
"""

from typing import Any
import pandas as pd
from api_auth import get_auth
from db_handler import DBConnection
from util import iter_hidroweb_date_chunks, request_with_auth_retry


def collect_simple_endpoint_data(
    *,
    url: str,
    table_name: str,
    inplace: bool,
    logger,
    params: dict[str, Any] | None = None,
) -> None:
    """
    Collect one-shot endpoint data and persist response items into DuckDB;
    """
    token = get_auth()
    if not token:
        logger.error("Failed to get authentication token")
        return

    headers = {"Authorization": f"Bearer {token}"}
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


def collect_chunked_endpoint_data(
    *,
    url: str,
    station_code: str,
    start_date: str,
    end_date: str,
    table_name: str,
    inplace: bool,
    logger,
    date_filter_type: str = "DATA_LEITURA",
    station_param_name: str = "Código da Estação",
    date_filter_param_name: str = "Tipo Filtro Data",
    search_date_param_name: str = "Data de Busca (yyyy-MM-dd)",
    range_param_name: str = "Range Intervalo de busca",
    extra_params: dict[str, Any] | None = None,
) -> None:
    """
    Collect endpoint data in date chunks while respecting API max-range limits;
    """
    token = get_auth()
    if not token:
        logger.error("Failed to get authentication token")
        return

    headers = {"accept": "*/*", "Authorization": f"Bearer {token}"}
    all_dataframes: list[pd.DataFrame] = []
    chunk_number = 1

    # Chunks are generated to guarantee each call stays under API date limits;
    for chunk in iter_hidroweb_date_chunks(start_date, end_date):
        search_date = chunk["start_date"].strftime("%Y-%m-%d")
        range_days = chunk["range_days"]
        actual_chunk_days = chunk["actual_chunk_days"]

        params: dict[str, Any] = {
            station_param_name: station_code,
            date_filter_param_name: date_filter_type,
            search_date_param_name: search_date,
            range_param_name: range_days,
        }
        if extra_params:
            params.update(extra_params)

        logger.info(
            "Chunk %s: %s | range %s | days %s",
            chunk_number,
            search_date,
            range_days,
            actual_chunk_days,
        )
        response, headers = request_with_auth_retry(
            url=url,
            headers=headers,
            params=params,
            get_auth_token=get_auth,
            request_logger=logger,
        )

        if response.status_code != 200:
            logger.error("Chunk %s failed with status code: %s", chunk_number, response.status_code)
            logger.error("Response text: %s", response.text)
            chunk_number += 1
            continue

        payload = response.json()
        if "items" in payload and payload["items"]:
            all_dataframes.append(pd.DataFrame(payload["items"]))
            logger.info("Chunk %s collected successfully", chunk_number)
        else:
            logger.info("Chunk %s returned no items", chunk_number)
        chunk_number += 1

    if not all_dataframes:
        logger.warning("No data collected for endpoint '%s'", url)
        return

    combined_df = pd.concat(all_dataframes, ignore_index=True)
    db_handler = DBConnection()
    db_handler.write(combined_df, table_name, inplace=inplace)
    logger.info("Collected %s records and saved to '%s'", len(combined_df), table_name)
