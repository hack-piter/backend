import logging
import os
import re

import boto3
from botocore.client import Config


class MinIOClient:
    client = boto3.client

    def __init__(self):
        self.logger = None
        self.endpoint = None
        self.access_key = None
        self.secret_key = None
        self.client = None

    def configure(self, endpoint, access_key, secret_key):
        self.logger = logging.getLogger(__name__)
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.client = boto3.client('s3',
                                   aws_access_key_id=access_key,
                                   aws_secret_access_key=secret_key,
                                   endpoint_url=endpoint,
                                   config=Config(signature_version='s3v4'))

    def upload_file(self, bucket_name, object_name, file):
        """
        Загрузить файл в MinIO

        :param bucket_name: Имя бакета
        :param file: Файл
        :param object_name: Имя объекта в MinIO
        """
        try:
            self.client.put_object(Body=file, Bucket=bucket_name, Key=object_name)
            self.logger.info(f"Файл {object_name} загружен в MinIO")
            return bucket_name,  object_name
        except Exception as e:
            self.logger.info(f"Ошибка загрузки файла: {e}")

    def download_file(self, bucket_name, object_name):
        """
        Скачать файл из MinIO

        :param bucket_name: Имя бакета
        :param object_name: Имя объекта в MinIO
        :param file_path: Путь к файлу на локальной машине
        """
        try:
            obj = self.client.get_object(Bucket=bucket_name, Key=object_name)
            file_path = re.sub(r'\d{4}/\d{2}/\d{2}/', '', object_name)
            with open(file_path, 'wb') as f:
                f.write(obj['Body'].read())
            self.logger.info(f"Файл {object_name} скачан из MinIO как {file_path}")
            return object_name, file_path
        except Exception as e:
            self.logger.info(f"Ошибка скачивания файла: {e}")
            raise Exception(e)

    def get_file(self, bucket_name, object_name):
        """
        Взять файл из MinIO

        :param bucket_name: Имя бакета
        :param object_name: Имя объекта в MinIO
        """
        try:
            obj = self.client.get_object(Bucket=bucket_name, Key=object_name)
            print(obj)
            return obj
        except Exception as e:
            self.logger.info(f"Ошибка скачивания файла: {e}")

    def list_buckets(self):
        """
        Список всех бакетов в MinIO
        """
        try:
            buckets = self.client.list_buckets()
            for bucket in buckets['Buckets']:
                self.logger.info(bucket['Name'])

        except Exception as e:
            self.logger.info(f"Ошибка получения списка бакетов: {e}")

    def list_objects(self, bucket_name):
        """
        Список всех объектов в бакете

        :param bucket_name: Имя бакета
        """
        try:
            objects = self.client.list_objects(Bucket=bucket_name)
            for obj in objects['Contents']:
                self.logger.info(obj['Key'])
            return objects
        except Exception as e:
            self.logger.info(f"Ошибка получения списка объектов: {e}")


endpoint = os.getenv("MINIO_ENDPOINT") or "http://localhost:9000"
access_key = os.getenv("MINIO_ACCESS_KEY") or "minio-access-key"
secret_key = os.getenv("MINIO_SECRET_KEY") or "minio-secret-key"
minio_client = MinIOClient()
minio_client.configure(endpoint, access_key, secret_key)
if __name__ == "__main__":
    print(minio_client.list_buckets())


