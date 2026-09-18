from dotenv import load_dotenv
import os

load_dotenv()

def get_s3_connection_options():
    return {
        'access_key': os.getenv('MINIO_ACCESS_KEY_RAW'),
        'secret_key': os.getenv('MINIO_SECRET_KEY_RAW'),
        'endpoint': os.getenv('MINIO_ENDPOINT_RAW'),
    }