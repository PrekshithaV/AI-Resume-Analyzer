import uuid
from backend.config import get_settings

settings = get_settings()


def upload_file_to_blob(file_bytes: bytes, filename: str, content_type: str) -> str:
    try:
        from azure.storage.blob import BlobServiceClient, ContentSettings
        client = BlobServiceClient.from_connection_string(
            settings.azure_storage_connection_string
        )
        container = client.get_container_client(settings.azure_container_name)
        try:
            container.create_container()
        except Exception:
            pass
        blob_name = f"{uuid.uuid4()}-{filename}"
        blob_client = container.get_blob_client(blob_name)
        blob_client.upload_blob(
            file_bytes,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type),
        )
        return blob_client.url
    except Exception as e:
        print(f"[WARN] Azure upload skipped: {e}")
        return ""
