from boto3 import client
from dotenv import dotenv_values, load_dotenv
from redshift_connector import connect
import os
from os import environ

from extract import (
    create_directory_if_not_exists,
    return_truck_data_files,
    download_truck_data_files
)

from transform import (
    clean_and_combine_batch_data
)

from load import (
    populate_dim_trucks,
    populate_fact_transactions
)


def delete_folder(folder_path):
    """Deletes a folder and its contents"""
    try:
        for root, dirs, files in os.walk(folder_path, topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                os.rmdir(dir_path)
        os.rmdir(folder_path)
        print(f"Folder '{folder_path}' and its contents deleted successfully.")
    except Exception as e:
        print(f"Error deleting folder '{folder_path}': {e}")


if __name__ == "__main__":

    # Extract:

    load_dotenv()

    config = {}

    config["DB_PASSWORD"] = environ.get("DB_PASSWORD")
    config["DB_NAME"] = environ.get("DB_NAME")
    config["DB_USER"] = environ.get("DB_USER")
    config["DB_HOST"] = environ.get("DB_HOST")
    config["DB_PORT"] = environ.get("DEB_PORT")

    config["ACCESS_KEY_ID"] = environ.get("ACCESS_KEY_ID")
    config["SECRET_ACCESS_KEY"] = environ.get("SECRET_ACCESS_KEY")

    config["BUCKET_NAME"] = environ.get("BUCKET_NAME")

    s3 = client("s3", aws_access_key_id=config["ACCESS_KEY_ID"],
                aws_secret_access_key=config["SECRET_ACCESS_KEY"])
    
    bucket_name = config["BUCKET_NAME"]

    objects_list = return_truck_data_files(s3, bucket_name)

    download_truck_data_files(s3, bucket_name, objects_list)

    # Transform:

    batch_input_directory = "./pipeline/batch_data/"
    batch_required_folder = "./pipeline/combined_batch_data"
    batch_output_file_path = "./pipeline/combined_batch_data/combined_batch_data.parquet"

    create_directory_if_not_exists(batch_required_folder)

    clean_and_combine_batch_data(batch_input_directory, batch_output_file_path)
    
    # Load:

    # parser = argparse.ArgumentParser()
    # parser.add_argument('--drop-tables', action='store_true', help='Drop all tables from the database')
    # args = parser.parse_args()

    conn = connect(database=config["DB_NAME"],
                   user=config["DB_USER"],
                   password=config["DB_PASSWORD"],
                   host=config["DB_HOST"],
                   port=config["DB_PORT"])
    
    with conn.cursor() as cur:
        cur.execute("SET search_path TO sigma_annie_schema")

    # schema_sql_file = "./pipeline/food_truck_db_schema.sql"

    truck_data_excel_file = "./pipeline/truck_metadata/details.xlsx"

    combined_batch_data = "./pipeline/combined_batch_data/combined_batch_data.parquet"

    # if args.drop_tables:
    #     drop_all_tables(conn)
    
    # create_all_tables(conn, schema_sql_file)

    # populate_dim_trucks(conn, truck_data_excel_file)

    # populate_dim_types(conn)

    populate_fact_transactions(conn, combined_batch_data)

    delete_folder(batch_input_directory)

    delete_folder(batch_required_folder)

    print("Hi")