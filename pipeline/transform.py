import pandas as pd
import pyarrow.parquet as pq
import os
from datetime import datetime, timedelta, timezone
import pytz

def create_directory_if_not_exists(directory_path: str):
    """Creates the directory if it doesn't exist"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def read_parquet_file(file_path):
    """Reads a Parquet file and returns the DataFrame"""
    return pd.read_parquet(file_path)


def read_csv_file(file_path):
    """Reads a Parquet file and returns the DataFrame"""
    return pd.read_csv(file_path)


def add_truck_id(df, truck_id):
    """Adds 'TruckID' column to the DataFrame"""
    df['TruckID'] = truck_id
    return df


def clean_data(df):
    """
    Removes empty values and values of the wrong data type
    from each column
    """
    df['total'] = pd.to_numeric(df['total'], errors='coerce')
    df = df.dropna(subset=['total'])
    df = df[df['total'] != 0]

    df['TruckID'] = df['TruckID'].astype(int)
    df = df.dropna(subset=['TruckID'])

    df['type'] = df['type'].astype(str).str.lower()

    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['timestamp'])

    return df


def remove_dodgy_values_from_data(df):
    """
    Removes suspicious values from the data
    (Negative 'total' values, 'total' values over £1000, 
    and data from the future)
    """
    df = df[df['total'] < 1000]
    df = df[df['total'] > 0]

    if df['timestamp'].dt.tz is None:
        df['timestamp'] = df['timestamp'].dt.tz_localize('UTC') 

    else:
        df['timestamp'] = df['timestamp'].dt.tz_convert('UTC')
    
    df = df[df['timestamp'] < pd.Timestamp.now(tz='UTC')]

    return df


def combine_historical_data_files(input_dir, output_file):
    """
    Loads and combines relevant files from the data/ folder.
    Produces a single combined file in the data/ folder.
    """
    historical_df = pd.DataFrame()

    for filename in os.listdir(input_dir):

        if filename.endswith(".parquet"):

            truck_id = (filename.split('.')[0]).split('_')[-1]
            file_path = os.path.join(input_dir, filename)
            df = read_parquet_file(file_path)
            df = add_truck_id(df, truck_id)
            df = clean_data(df)
            df = remove_dodgy_values_from_data(df)
            historical_df = pd.concat([historical_df, df], ignore_index=True)

        else:

            raise ValueError("All files to be combined (those in the input directory)"
                             + " must be .parquet files")
        
    historical_df.to_parquet(output_file, index=False)


def clean_and_combine_batch_data(input_dir, output_file):
    """
    Loads and combines latest batch of .csv files 
    """
    combined_batch_df = pd.DataFrame()

    for filename in os.listdir(input_dir):

        if filename.endswith(".csv"):

            truck_id = filename.split('_')[1][1]
            file_path = os.path.join(input_dir, filename)
            df = read_csv_file(file_path)
            df = add_truck_id(df, truck_id)
            df = clean_data(df)
            df = remove_dodgy_values_from_data(df)
            combined_batch_df = pd.concat([combined_batch_df, df], ignore_index=True)

        else:

            raise ValueError("All batch data files to be combined (those in the input directory)"
                             + " must be .csv files")
        
    combined_batch_df.to_parquet(output_file, index=False)


if __name__ == "__main__":

    hist_input_directory = "./pipeline/historical_data/"
    hist_required_folder = "./pipeline/combined_historical_data"
    hist_output_file_path = "./pipeline/combined_historical_data/combined_historical_data.parquet"

    batch_input_directory = "./pipeline/batch_data/"
    batch_required_folder = "./pipeline/combined_batch_data"
    batch_output_file_path = "./pipeline/combined_batch_data/combined_batch_data.parquet"

    create_directory_if_not_exists(hist_required_folder)

    combine_historical_data_files(hist_input_directory, hist_output_file_path)

    create_directory_if_not_exists(batch_required_folder)

    clean_and_combine_batch_data(batch_input_directory, batch_output_file_path)