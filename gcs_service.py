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

gcs_service = GCSStorageManager()
