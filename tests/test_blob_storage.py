from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from azure.core.exceptions import ResourceExistsError

from backend_fastapi.blob_storage import BlobStorage

from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
)


@pytest.fixture
def storage(monkeypatch):
    monkeypatch.setenv(
        "AZURE_STORAGE_CONNECTION_STRING",
        "test-connection-string",
    )
    monkeypatch.setenv(
        "AZURE_STORAGE_CONTAINER_NAME",
        "resumes",
    )

    with patch(
        "backend_fastapi.blob_storage.BlobServiceClient"
    ) as mock_service:
        instance = BlobStorage()
        yield instance, mock_service


def test_missing_connection_string(monkeypatch):
    monkeypatch.delenv(
        "AZURE_STORAGE_CONNECTION_STRING",
        raising=False,
    )

    with pytest.raises(ValueError, match="missing"):
        BlobStorage()


def test_upload_success(storage):
    instance, mock_service = storage
    blob_key = "user-1/resume-v1.pdf"
    stream = BytesIO(b"PDF content")

    result = instance.upload(blob_key, stream)

    assert result == blob_key

    mock_service.from_connection_string.return_value \
        .get_container_client.return_value \
        .upload_blob.assert_called_once_with(
            name=blob_key,
            data=stream,
            overwrite=False,
            content_settings=None,
        )


def test_duplicate_blob_key(storage):
    instance, mock_service = storage

    container = (
        mock_service.from_connection_string.return_value
        .get_container_client.return_value
    )
    container.upload_blob.side_effect = ResourceExistsError(
        message="Blob already exists"
    )

    with pytest.raises(ValueError, match="already exists"):
        instance.upload(
            "user-1/resume-v1.pdf",
            BytesIO(b"PDF content"),
        )

def test_download_success(storage):
    instance, mock_service = storage

    container = (
        mock_service.from_connection_string.return_value
        .get_container_client.return_value
    )

    payload = b"test PDF content"
    container.download_blob.return_value.readall.return_value = payload

    result = instance.download("user-1/resume-v1.pdf")

    assert result == payload
    container.download_blob.assert_called_once_with(
        "user-1/resume-v1.pdf"
    )


def test_download_missing_blob(storage):
    instance, mock_service = storage

    container = (
        mock_service.from_connection_string.return_value
        .get_container_client.return_value
    )
    container.download_blob.side_effect = ResourceNotFoundError(
        message="Blob not found"
    )

    with pytest.raises(FileNotFoundError, match="Blob not found"):
        instance.download("missing.pdf")


def test_upload_azure_failure(storage):
    instance, mock_service = storage

    container = (
        mock_service.from_connection_string.return_value
        .get_container_client.return_value
    )
    container.upload_blob.side_effect = HttpResponseError(
        message="Azure service unavailable"
    )

    with pytest.raises(RuntimeError, match="Azure Blob upload failed"):
        instance.upload("resume.pdf", BytesIO(b"PDF"))


@pytest.mark.parametrize("blob_key", ["", None])
def test_invalid_blob_key(storage, blob_key):
    instance, _ = storage

    with pytest.raises(ValueError, match="Blob key cannot be empty"):
        instance.upload(blob_key, BytesIO(b"PDF"))

    with pytest.raises(ValueError, match="Blob key cannot be empty"):
        instance.download(blob_key)

def test_download_azure_failure(storage):
    instance, mock_service = storage

    container = (
        mock_service.from_connection_string.return_value
        .get_container_client.return_value
    )

    container.download_blob.side_effect = HttpResponseError(
        message="Azure service unavailable"
    )

    with pytest.raises(
        RuntimeError,
        match="Azure Blob download failed",
    ):
        instance.download("user-1/resume-v1.pdf")