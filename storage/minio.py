from django.conf import settings
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from urllib3.response import BaseHTTPResponse

from clients.minio import CustomClientMinio


@deconstructible
class MinioStorage(Storage):
    def __init__(self):
        self.client = CustomClientMinio().client
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    def _open(self, name: str) -> BaseHTTPResponse:
        return self.client.get_object(self.bucket_name, name)

    def _save(self, name, content):
        self.client.put_object(
            bucket_name=self.bucket_name,
            object_name=name,
            data=content.file,
            length=content.size,
            content_type=content.content_type
        )
        return name

    def url(self, name):
        return f"https://play.min.io/{self.bucket_name}/{name}"

    def exists(self, name):
        try:
            self.client.stat_object(self.bucket_name, name)
            return True
        except Exception:
            return False
