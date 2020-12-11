# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 16:07:04 2020

@author: AndrewPC
"""
import asyncio
import logging
from concurrent.futures.process import ProcessPoolExecutor
from pathlib import Path
from typing import Tuple, Dict, List, Any
import nest_asyncio         
nest_asyncio.apply()

import requests
from requests import Session

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel("INFO")


def download_dataset_file(
    session: Session,
    base_url: str,
    dataset_name: str,
    dataset_version: str,
    filename: str,
    directory: str,
) -> Tuple[bool, str]:
    endpoint = f"{base_url}/datasets/{dataset_name}/versions/{dataset_version}/files/{filename}/url"
    get_file_response = session.get(endpoint)

    # retrieve download URL for dataset file
    if get_file_response.status_code != 200:
        logger.warning(f"Unable to get file: {filename}")
        logger.warning(get_file_response.content)
        return False, filename

    # use download URL to GET dataset file. We don't need to set the 'Authorization' header,
    # The presigned download URL already has permissions to GET the file contents
    download_url = get_file_response.json().get("temporaryDownloadUrl")
    download_dataset_file_response = requests.get(download_url)

    if download_dataset_file_response.status_code != 200:
        logger.warning(f"Unable to download file: {filename}")
        logger.warning(download_dataset_file_response.content)
        return False, filename

    # write dataset file to disk
    p = Path(f"{directory}/{filename}")
    p.write_bytes(download_dataset_file_response.content)

    logger.info(f"Downloaded dataset file '{filename}'")
    return True, filename


def list_dataset_files(
    session: Session,
    base_url: str,
    dataset_name: str,
    dataset_version: str,
    params: Dict[str, str],
) -> Tuple[List[str], Dict[str, Any]]:
    logger.info(f"Retrieve dataset files with query params: {params}")

    list_files_endpoint = (
        f"{base_url}/datasets/{dataset_name}/versions/{dataset_version}/files"
    )
    list_files_response = session.get(list_files_endpoint, params=params)

    if list_files_response.status_code != 200:
        raise Exception("Unable to list initial dataset files")

    try:
        list_files_response_json = list_files_response.json()
        dataset_files = list_files_response_json.get("files")
        dataset_filenames = list(map(lambda x: x.get("filename"), dataset_files))
        return dataset_filenames, list_files_response_json
    except Exception as e:
        logger.error(e)
        raise Exception(e)


async def main():
    api_key = "5e554e19274a9600012a3eb1b626f95624124cf89e9b5d74c3304520" #This API key is for bulk downloads provided by KNMI(Available till 25 May 2021)
    dataset_name = "cesar_surface_meteo_lb1_t10"
    dataset_version = "v1.0"
    base_url = "https://api.dataplatform.knmi.nl/open-data"

    download_directory = "E:\Climate Physics\MAIO\Cabauw Large scale circulation"

    # Make sure to send the API key with every HTTP request
    session = requests.Session()
    session.headers.update({"Authorization": api_key})

    # Verify that the download directory exists
    if not Path(download_directory).is_dir() or not Path(download_directory).exists():
        raise Exception(f"Invalid or non-existing directory: {download_directory}")

    filenames = []

    start_after_filename = " "
    max_keys = 500

    # Use the API to get a list of all dataset filenames
    while True:
        # Retrieve dataset files after given filename
        dataset_filenames, response_json = list_dataset_files(
            session,
            base_url,
            dataset_name,
            dataset_version,
            {"maxKeys": f"{max_keys}", "startAfterFilename": start_after_filename},
        )

        # Store filenames
        filenames += dataset_filenames

        # If the result is not truncated, we retrieved all filenames
        is_truncated = response_json.get("isTruncated")
        if not is_truncated:
            logger.info("Retrieved names of all dataset files")
            break

        start_after_filename = dataset_filenames[-1]
    
    logger.info(f"Number of files to download: {len(filenames)}")
    loop = asyncio.get_event_loop()
    
    # Allow up to 20 separate processes to download dataset files concurrently
    executor = ProcessPoolExecutor(max_workers=20)
    futures = []

    # Create tasks that download the dataset files
    for dataset_filename in filenames:
        # Create future for dataset file
        future = loop.run_in_executor(
            executor,
            download_dataset_file,
            session,
            base_url,
            dataset_name,
            dataset_version,
            dataset_filename,
            download_directory,
        )
        futures.append(future)

    # Wait for all tasks to complete and gather the results
    future_results = await asyncio.gather(*futures)
    logger.info(f"Finished '{dataset_name}' dataset download")

    failed_downloads = list(filter(lambda x: not x[0], future_results))

    if len(failed_downloads) > 0:
        logger.info("Failed to download the following dataset files")
        logger.info(list(map(lambda x: x[1], failed_downloads)))


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
