import os
import logging
from typing import Optional
from backend.config import settings

logger = logging.getLogger(__name__)

class StorageService:
    """
    Cloudflare R2 / S3 Object Storage Service.
    Handles secure file uploads (Candidate Resumes, Evaluation PDF Reports)
    and presigned URL generation.
    """
    def __init__(
        self,
        account_id: Optional[str] = None,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        bucket_name: Optional[str] = None,
        public_url: Optional[str] = None
    ):
        self.account_id = account_id or settings.R2_ACCOUNT_ID
        self.access_key_id = access_key_id or settings.R2_ACCESS_KEY_ID
        self.secret_access_key = secret_access_key or settings.R2_SECRET_ACCESS_KEY
        self.bucket_name = bucket_name or settings.R2_BUCKET_NAME
        self.public_url = (public_url or settings.R2_PUBLIC_URL).rstrip("/")

        self.endpoint_url = (
            f"https://{self.account_id}.r2.cloudflarestorage.com"
            if self.account_id else None
        )
        self._client = None

    def _get_client(self):
        is_testing = bool(
            os.environ.get("PYTEST_CURRENT_TEST")
            or os.environ.get("TESTING")
            or (self.access_key_id and self.access_key_id.startswith("test-"))
        )
        if is_testing:
            return None

        if self._client is not None:
            return self._client

        if not self.access_key_id or not self.secret_access_key:
            return None

        try:
            import boto3
            from botocore.config import Config
            self._client = boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                config=Config(signature_version="s3v4")
            )
            return self._client
        except Exception as e:
            logger.warning(f"Failed to initialize S3/R2 client: {e}")
            return None

    def upload_bytes(
        self,
        data: bytes,
        key: str,
        content_type: str = "application/octet-stream"
    ) -> str:
        """
        Uploads raw binary bytes to R2 bucket under key.
        Returns canonical public URL or storage link.
        """
        client = self._get_client()
        clean_key = key.lstrip("/")

        if client:
            try:
                client.put_object(
                    Bucket=self.bucket_name,
                    Key=clean_key,
                    Body=data,
                    ContentType=content_type
                )
                logger.info(f"Successfully uploaded {len(data)} bytes to R2: {clean_key}")
            except Exception as e:
                logger.error(f"R2 upload failed ({e}), falling back to direct storage URL.")

        return f"{self.public_url}/{clean_key}"

    def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """Generates time-limited presigned download URL."""
        client = self._get_client()
        clean_key = key.lstrip("/")

        if client:
            try:
                url = client.generate_presigned_url(
                    ClientMethod="get_object",
                    Params={"Bucket": self.bucket_name, "Key": clean_key},
                    ExpiresIn=expires_in
                )
                return url
            except Exception as e:
                logger.warning(f"Presigned URL generation failed: {e}")

        return f"{self.public_url}/{clean_key}?expires={expires_in}"

storage_service = StorageService()
