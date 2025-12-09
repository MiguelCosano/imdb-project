"""Extract data from IMDb datasets"""
import logging
from pathlib import Path
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import requests
from config.constants import MAX_RETRIES, DOWNLOAD_CHUNK_SIZE, IMDB_URL
from alive_progress import alive_bar

class DataExtractor:
    def __init__(self, base_url: str = IMDB_URL):
        self.base_url = base_url
        
    def should_download(self, filename: str) -> bool:
        """Check if file needs to be downloaded"""
        url = f"{self.base_url}{filename}"
        local_path = Path(f"data/{filename}")
        logging.info(f"Checking for updates to {filename}")
        if not local_path.exists():
            logging.info(f"{filename} does not exist locally, will download")
            return True
        try:
            resp = requests.head(url, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"HEAD request failed for {url}: {e}")
            return False
            
        last_mod = resp.headers.get("Last-Modified")
        if not last_mod:
            logging.warning(f"No Last-Modified header, downloading anyway")
            return True
            
        try:
            remote_date = parsedate_to_datetime(last_mod)
            if remote_date.tzinfo is None:
                remote_date = remote_date.replace(tzinfo=timezone.utc)
        except Exception as e:
            logging.error(f"Failed to parse Last-Modified: {e}")
            return True
        
        local_date = datetime.fromtimestamp(
            local_path.stat().st_mtime, tz=timezone.utc
        )
        if remote_date <= local_date:
            logging.info(f"No changes in {filename}")
            return False
                
        return True
        
    def download(self, filename: str) -> bool:
        """Download file with retry logic"""
        url = f"{self.base_url}{filename}"
        project_root = Path(__file__).resolve().parents[1]
        data_dir = project_root / "data"
        local_path = data_dir / filename
        temp_path = local_path.with_suffix(local_path.suffix + ".tmp")
        
        for attempt in range(MAX_RETRIES):
            try:
                r = requests.get(url, stream=True, timeout=30)
                r.raise_for_status()
                
                total_size = int(r.headers.get('content-length', 0))
                downloaded_size = 0
                with alive_bar(total_size or None, title=f"Downloading {filename}", 
                          unit='B', force_tty=True) as bar:
                    with open(temp_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                            if chunk:
                                f.write(chunk)
                                downloaded_size += len(chunk)
                                bar(len(chunk))
            
                if downloaded_size == 0:
                    logging.error("Downloaded file is empty")
                    temp_path.unlink(missing_ok=True)
                    return False
                
                temp_path.replace(local_path)
                logging.info(f"{local_path}: Downloaded ({downloaded_size:,} bytes)")
                return True
                
            except requests.RequestException as e:
                logging.warning(f"Attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
                temp_path.unlink(missing_ok=True)
                if attempt == MAX_RETRIES - 1:
                    logging.error(f"Failed after {MAX_RETRIES} attempts")
                    return False
        
        return False
