import logging
import pandas as pd
import requests
from typing import Iterator
from utils.constants import IMDB_URL, CHUNK_SIZE
from utils.metadata import load_metadata, save_metadata, should_reload


class DataExtractor:
    """Extract raw data from IMDb using pandas built-in URL streaming."""

    def __init__(self, base_url: str = IMDB_URL):
        self.base_url = base_url

    def should_download(self, filename: str) -> bool:
        """Check if file needs to be downloaded based on ETag comparison"""
        url = f"{self.base_url}{filename}"
        stored_metadata = load_metadata()
        logging.info(f"Checking for updates to {filename}")

        return should_reload(stored_metadata, url)

    def read_chunks(self, filename: str, cols: list[str], dtype: dict) -> Iterator[pd.DataFrame]:
        """
        Read file in chunks directly from URL and streams it

        Args
        ----------
            filename: IMDb filename (e.g., 'name.basics.tsv.gz')
            cols: Columns that should be used from the downloaded file
            dtype: Type association for the data of the retrieved columns

        Yields
        ----------
            pd.DataFrame chunks from the TSV file

        """
        url = f"{self.base_url}{filename}"

        logging.info(f"Streaming {filename} from {url}")

        try:
            etag = self._get_file_metadata(url)

            for chunk in pd.read_csv(
                url,
                sep="\t",
                chunksize=CHUNK_SIZE,
                na_values=["\\N"],
                keep_default_na=True,
                compression="gzip",
                on_bad_lines="warn",
                engine="c",
                usecols=cols,
                dtype=dtype
            ):
                yield chunk

            save_metadata(filename, etag)

            logging.info(f"Successfully streamed {filename}")

        except Exception as e:
            logging.error(f"Failed to stream {filename}: {e}")
            raise

    def _get_file_metadata(self, url: str) -> str:
        """Get ETag and file size using HEAD request (doesn't download file)"""
        try:
            response = requests.head(url, timeout=10)
            response.raise_for_status()

            etag = response.headers.get("ETag")

            logging.debug(f"Metadata - ETag: {etag}")

            return etag

        except Exception as e:
            logging.warning(f"Failed to get metadata: {e}")
            return None, 0
