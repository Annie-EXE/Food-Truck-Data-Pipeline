from boto3 import client
from botocore.client import BaseClient
from dotenv import dotenv_values
import os
from datetime import datetime, timedelta, timezone


def create_directory_if_not_exists(directory_path: str):
    """Creates the directory if it doesn't exist"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def download_file_from_bucket(s3: str, bucket_name: str, file):
    """Downloads an object file from a bucket"""
    object_key = file["Key"]

    if "historical" in object_key:
        create_directory_if_not_exists("./pipeline/historical_data")
        filename = os.path.basename(object_key)
        s3.download_file(bucket_name, object_key, f"./pipeline/historical_data/{filename}")

    elif "metadata" in object_key:
        create_directory_if_not_exists("./pipeline/truck_metadata")
        filename = os.path.basename(object_key)
        s3.download_file(bucket_name, object_key, f"./pipeline/truck_metadata/{filename}")
    
    last_modified = (file["LastModified"]).astimezone(timezone.utc)

    current_time = datetime.now().astimezone(timezone.utc)
    time_threshold = current_time - timedelta(hours=3)

    if object_key.startswith("trucks/") and last_modified >= time_threshold:
        create_directory_if_not_exists("./pipeline/batch_data")
        filename = os.path.basename(object_key)
        s3.download_file(bucket_name, object_key, f"./pipeline/batch_data/{filename}")


def return_truck_data_files(s3: BaseClient, bucket_name: str):
    """Returns all items in bucket"""
    response = s3.list_objects_v2(Bucket=bucket_name)["Contents"]

    return response


def download_truck_data_files(s3: BaseClient, bucket_name: str, files: list):
    """Downloads relevant files from S3 to a data/ folder."""

    for file in files:

        download_file_from_bucket(s3, bucket_name, file)


if __name__ == "__main__":

    config = dotenv_values()

    s3 = client("s3", aws_access_key_id=config["ACCESS_KEY_ID"],
                aws_secret_access_key=config["SECRET_ACCESS_KEY"])
    
    bucket_name = config["BUCKET_NAME"]

    objects_list = return_truck_data_files(s3, bucket_name)

    download_truck_data_files(s3, bucket_name, objects_list)
