from minio import Minio
from django.conf import settings


class Singleton:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls)
        return cls._instance

    @staticmethod
    def _load_client():
        pass


class CustomClientMinio(Singleton):
    def __init__(self):
        self.client = self._load_client()

    @staticmethod
    def _load_client() -> Minio:
        return Minio(
            "play.min.io",
            access_key=settings.AWS_ACCESS_KEY_ID,
            secret_key=settings.AWS_SECRET_ACCESS_KEY
        )
