import os
from typing import BinaryIO

from azure.core.exceptions import (
    ResourceExistsError,
    HttpResponseError,
)
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError

class BlobStorage:
    def __init__(self):
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        container_name = os.getenv(
            "AZURE_STORAGE_CONTAINER_NAME", "resumes"
        )

        if not connection_string:
            raise ValueError(
                "AZURE_STORAGE_CONNECTION_STRING is missing"
            )

        self.client = BlobServiceClient.from_connection_string(
            connection_string
        )
        self.container = self.client.get_container_client(
            container_name
        )

    def upload(self, blob_key: str, file: BinaryIO) -> str:
        if not blob_key:
            raise ValueError("Blob key cannot be empty")

        try:
            self.container.upload_blob(
                name=blob_key,
                data=file,
                overwrite=False,
                content_settings=None,
            )
            return blob_key

        except ResourceExistsError as exc:
            raise ValueError(
                f"Blob already exists: {blob_key}"
            ) from exc

        except HttpResponseError as exc:
            raise RuntimeError(
                "Azure Blob upload failed"
            ) from exc

    def download(self, blob_key: str) -> bytes:
        if not blob_key:
            raise ValueError("Blob key cannot be empty")

        try:
            downloader = self.container.download_blob(blob_key)
            return downloader.readall()

        except ResourceNotFoundError as exc:
            raise FileNotFoundError(
                f"Blob not found: {blob_key}"
            ) from exc

        except HttpResponseError as exc:
            raise RuntimeError(
                "Azure Blob download failed"
            ) from exc