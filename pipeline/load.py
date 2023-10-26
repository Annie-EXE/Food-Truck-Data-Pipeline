import redshift_connector
from redshift_connector import connect, Connection
from dotenv import dotenv_values
import pandas as pd
import pyarrow
import argparse


def create_all_tables(conn: Connection, schema_sql_file: str):
    """Creates tables according to schema 
    contained in given .sql file"""
    with open(schema_sql_file, 'r') as f:
        tables_query = f.read()
    
    statements = tables_query.split(';')

    executable_statements = []

    for statement in statements:

        statement = statement.strip()

        executable_statements.append(statement)

    with conn.cursor() as cur:

        for statement in executable_statements:

            if statement != '':

                cur.execute(statement)

    conn.commit()


def drop_all_tables(conn):
    """
    Drops the 3 mentioned tables
    """
    with conn.cursor() as cur:
        
        cur.execute(f"DROP TABLE IF EXISTS FACT_transactions")
        cur.execute(f"DROP TABLE IF EXISTS DIM_trucks")
        cur.execute(f"DROP TABLE IF EXISTS DIM_types")

    conn.commit()


def populate_dim_trucks(conn: Connection, truck_data_excel_file: str):
    """Uploads truck metadata to the database, from a .xlsx file"""
    df = pd.read_excel(truck_data_excel_file)

    df["HAS_CARD_READER"] = df["HAS_CARD_READER"].replace({"Yes": True, "No": False})

    with conn.cursor() as cur:

        for index, row in df.iterrows():

            name = row['NAME']
            description = row['DESCRIPTION']
            has_card_reader = row['HAS_CARD_READER']
            fsa_rating = row['FSA_RATING_22']

            insert_query = """
            INSERT INTO DIM_trucks (truck_name, truck_desc, truck_has_card_reader, truck_fsa_rating)
            VALUES (%s, %s, %s, %s)
            """

            cur.execute("SELECT * FROM dim_trucks;")

            trucks = cur.fetchall()

            if name not in [truck[1] for truck in trucks]:

                cur.execute(insert_query, (name, description, has_card_reader, fsa_rating))
            
    conn.commit()


def populate_dim_types(conn: Connection):
    """
    Adds 2 rows to the DIM_types table, if
    they are not already there
    """
    with conn.cursor() as cur:

        cur.execute("SELECT * FROM DIM_Types")

        types = cur.fetchall()

        if "card" not in [types[1] for type in types]:
            cur.execute("INSERT INTO DIM_types (type_desc) VALUES ('card')")
        
        if "cash" not in [types[1] for type in types]:
            cur.execute("INSERT INTO DIM_types (type_desc) VALUES ('cash')")
    
    conn.commit()


def populate_fact_transactions(conn: Connection, parquet_file: str):
    """
    Reads from parquet files and from DIM_trucks and
    DIM_types, to populate the FACT_transactions table
    """
    df = pd.read_parquet(parquet_file)

    df.rename(columns={'type': 'type_desc'}, inplace=True)

    df['timestamp'] = pd.to_datetime(df['timestamp'])

    df['TruckID'] = df['TruckID'].astype(int)

    records_fact_transactions = df[['total', 'type_desc', 'TruckID', 'timestamp']].values.tolist()

    insert_query = """
    INSERT INTO FACT_transactions (total, type_id, truck_id, transaction_time) 
    VALUES (%s, (SELECT type_id FROM DIM_types WHERE type_desc = %s), 
    (SELECT truck_id FROM DIM_trucks WHERE truck_id = %s), %s);
    """

    with conn.cursor() as cur:

        cur.executemany(insert_query, records_fact_transactions)

    conn.commit()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--drop-tables', action='store_true', help='Drop all tables from the database')
    args = parser.parse_args()

    config = dotenv_values()

    conn = connect(database=config["DB_NAME"],
                   user=config["DB_USER"],
                   password=config["DB_PASSWORD"],
                   host=config["DB_HOST"],
                   port=config["DB_PORT"])
    
    with conn.cursor() as cur:
        cur.execute("SET search_path TO sigma_annie_schema")

    schema_sql_file = "./pipeline/food_truck_db_schema.sql"

    truck_data_excel_file = "./pipeline/truck_metadata/details.xlsx"

    historical_parquet_file = "./pipeline/combined_historical_data/combined_historical_data.parquet"

    combined_batch_data_file = "./pipeline/combined_batch_data/combined_batch_data.parquet"
    
    if args.drop_tables:
        drop_all_tables(conn)
    
    create_all_tables(conn, schema_sql_file)

    populate_dim_trucks(conn, truck_data_excel_file)

    # populate_dim_types(conn)

    # populate_fact_transactions(conn, combined_batch_data_file)