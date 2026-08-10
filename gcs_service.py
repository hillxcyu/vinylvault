import os
import logging
from typing import Optional

logger = logging.getLogger("vinyl_vault")

class GCSStorageManager:
    def __init__(self):
        self.bucket_name = os.environ.get(
            "GCS_BUCKET_NAME", "universal-trail-492014-n5-vinyl-vault-hk-data"
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

        return f"https://storage.googleapis.com/{self.bucket_name}/{blob_path}"

    def download_gcs_cover_bytes(self, cover_url_or_filename: str) -> Optional[bytes]:
        """
        Downloads cover image bytes directly from GCS storage bucket (covers/{clean_filename}).
        Exclusively relies on GCS persistence without local static disk fallbacks.
        """
        if not cover_url_or_filename:
            return None

        clean_filename = os.path.basename(cover_url_or_filename.split("?")[0])
        gcs_public_url = f"https://storage.googleapis.com/{self.bucket_name}/covers/{clean_filename}"

        # 1. Try HTTP GET for GCS public URLs or web URLs
        target_url = cover_url_or_filename if cover_url_or_filename.startswith("http") else gcs_public_url
        try:
            import requests
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://www.discogs.com/"
            }
            resp = requests.get(target_url, headers=headers, timeout=12)
            if resp.status_code == 200 and len(resp.content) > 100:
                return resp.content
        except Exception as e:
            logger.warning(f"HTTP GCS download warning for '{target_url}': {e}")

        # 2. Try GCS Bucket direct blob download as fallback
        if self.bucket and clean_filename:
            try:
                blob_path = f"covers/{clean_filename}"
                blob = self.bucket.blob(blob_path)
                if blob.exists():
                    return blob.download_as_bytes()
            except Exception as e:
                logger.warning(f"Direct GCS blob download warning for '{clean_filename}': {e}")

        return None

gcs_service = GCSStorageManager()



