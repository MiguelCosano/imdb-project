import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
import requests

METADATA_FILE = Path(__file__).resolve().parent.parent / "data" / "metadata.json"


def load_metadata() -> dict:
    """
    Load metadata from JSON file

    Returns:
        Dict with filename as key and metadata dict as value
    """
    if METADATA_FILE.exists():
        try:
            return json.loads(METADATA_FILE.read_text())
        except Exception as e:
            logging.warning(f"Failed to load metadata: {e}")
            return {}
    return {}


def save_metadata(filename: str, etag: Optional[str]):
    """
    Save metadata after successful download

    Args:
        filename: File name (e.g., 'name.basics.tsv.gz')
        etag: ETag header from response
        size_bytes: File size in bytes
    """
    metadata = load_metadata()

    metadata[filename] = {
        "etag": etag
    }

    try:
        METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        METADATA_FILE.write_text(json.dumps(metadata, indent=2))
        logging.debug(f"Saved metadata for {filename}")
    except Exception as e:
        logging.error(f"Failed to save metadata: {e}")


def should_reload(stored_metadata: dict, url: str) -> bool:
    """
    Check if file needs re-download based on ETag comparison

    Args:
        stored_metadata: Previously loaded metadata dict
        url: Full URL to check

    Returns:
        True if file should be downloaded, False if unchanged
    """
    filename = url.split("/")[-1]

    if filename not in stored_metadata:
        logging.info(f"No metadata found for {filename}, will download")
        return True

    stored_etag = stored_metadata[filename].get("etag")

    if not stored_etag:
        logging.info(f"No ETag stored for {filename}, will download")
        return True

    try:
        response = requests.head(url, timeout=10)
        response.raise_for_status()
        current_etag = response.headers.get("ETag")

        if not current_etag:
            logging.warning(f"No ETag header from server for {filename}")
            return True

        if stored_etag == current_etag:
            logging.info(f"{filename} unchanged (ETag match)")
            return False
        else:
            logging.info(f"{filename} changed (ETag mismatch)")
            return True

    except requests.RequestException as e:
        logging.error(f"ETag check failed for {filename}: {e}")
        return True


def get_metadata_info(filename: str) -> Optional[dict]:
    """Get metadata for a specific file"""
    metadata = load_metadata()
    return metadata.get(filename)
