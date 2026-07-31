import os
import logging
from typing import Optional

logger = logging.getLogger("vinyl_vault")

class GCSStorageManager:
    def __init__(self):
        self.bucket_name = os.environ.get(
            "GCS_BUCKET_NAME", "universal-trail-492014-n5-vinyl-vault-data"
        )
        self.project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "universal-trail-492014-n5")
        self.client = None
        self.bucket = None
        self._init_gcs()

    def _init_gcs(self):
        try:
            from google.cloud import storage
            self.client = storage.Client(project=self.project_id)
            self.bucket = self.client.bucket(self.bucket_name)
            logger.info(f"GCS Storage client initialized for bucket: {self.bucket_name}")
        except Exception as e:
            logger.warning(f"GCS Storage client initialization warning (using local fallback): {e}")
            self.client = None
            self.bucket = None

    def upload_cover(
        self, file_bytes: bytes, filename: str, content_type: str = "image/jpeg"
    ) -> str:
        """
        Uploads image file_bytes to GCS bucket under covers/{filename}.
        Returns public GCS URL if uploaded, or local fallback path if GCS is unavailable.
        """
        clean_filename = os.path.basename(filename)
        blob_path = f"covers/{clean_filename}"

        if self.bucket:
            try:
                blob = self.bucket.blob(blob_path)
                blob.upload_from_string(file_bytes, content_type=content_type)
                try:
                    blob.make_public()
                except Exception:
                    pass
                gcs_url = f"https://storage.googleapis.com/{self.bucket_name}/{blob_path}"
                logger.info(f"Uploaded cover '{clean_filename}' to GCS: {gcs_url}")
                return gcs_url
            except Exception as e:
                logger.error(f"GCS cover upload error for '{clean_filename}': {e}")

        # Local disk fallback for development
        local_dir = os.path.join(os.path.dirname(__file__), "static", "extracted_covers")
        os.makedirs(local_dir, exist_ok=True)
        local_path = os.path.join(local_dir, clean_filename)
        try:
            with open(local_path, "wb") as f:
                f.write(file_bytes)
        except Exception as err:
            logger.error(f"Local cover write error: {err}")

        return f"/static/extracted_covers/{clean_filename}"

    def download_cover_bytes(self, cover_url: str) -> Optional[bytes]:
        """
        Downloads cover image bytes from HTTP URL, GCS bucket, or local disk fallback.
        """
        if not cover_url:
            return None

        clean_filename = os.path.basename(cover_url.split("?")[0])

        # 1. Try HTTP / HTTPS download
        if cover_url.startswith("http://") or cover_url.startswith("https://"):
            try:
                import requests
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                    "Referer": "https://www.discogs.com/"
                }
                resp = requests.get(cover_url, headers=headers, timeout=12)
                if resp.status_code == 200 and len(resp.content) > 100:
                    return resp.content
            except Exception as e:
                logger.warning(f"Failed HTTP download for '{cover_url}': {e}")

        # 2. Try GCS Bucket direct blob download
        if self.bucket and clean_filename:
            try:
                blob_path = f"covers/{clean_filename}"
                blob = self.bucket.blob(blob_path)
                if blob.exists():
                    return blob.download_as_bytes()
            except Exception as e:
                logger.warning(f"Failed GCS download for '{clean_filename}': {e}")

        # 3. Try Local Disk fallback
        local_path = os.path.join(os.path.dirname(__file__), "static", "extracted_covers", clean_filename)
        if os.path.exists(local_path):
            try:
                with open(local_path, "rb") as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Failed local file read for '{local_path}': {e}")

        return None

gcs_service = GCSStorageManager()

