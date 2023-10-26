from boto3 import client
import redshift_connector
from redshift_connector import connect, Connection
from dotenv import dotenv_values, load_dotenv
import pandas as pd
from os import environ
import datetime
from datetime import datetime, timedelta
import json


def total_transaction_value_all_trucks(conn):
    """
    Calculates total transaction value
    across all trucks, for the previous day
    """
    query = f"""
        SELECT ROUND(SUM(total), 2) AS total_transaction_value
        FROM FACT_transactions
        WHERE DATE(transaction_time) = DATE(CURRENT_DATE - 1);
        """

    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchone()


def transactions_per_truck(conn):
    """
    Calculates total transaction value
    and number of transactions for each
    truck, for the previous day
    """
    query = f"""
        SELECT
            t.truck_id,
            t.truck_name,
            ROUND(SUM(ft.total), 2) AS total_transaction_value,
            COUNT(ft.transaction_id) AS transaction_count
        FROM DIM_trucks t
        LEFT JOIN FACT_transactions ft ON t.truck_id = ft.truck_id
        WHERE DATE(ft.transaction_time) = DATE(CURRENT_DATE - 1)
        GROUP BY t.truck_id, t.truck_name;
        """
    
    with conn.cursor() as cur:
        cur.execute(query)
        results = cur.fetchall()
    
    formatted_results = [
        {'truck_id':truck_id, 'truck_name':truck_name, 'total_transaction_value':"{:.2f}".format(total_value), 'transaction_count':transaction_count}
        for truck_id, truck_name, total_value, transaction_count in results
    ]

    return formatted_results


def mean_and_median_transaction_value_per_truck(conn):
    """
    Calculates the mean and median
    transaction value for each truck,
    for the previous day
    """
    query = f"""
        SELECT
            t.truck_id,
            t.truck_name,
            ROUND(AVG(ft.total), 2) AS mean_transaction_value,
            ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ft.total), 2) AS median_transaction_value
        FROM DIM_trucks t
        LEFT JOIN FACT_transactions ft ON t.truck_id = ft.truck_id
        WHERE DATE(ft.transaction_time) = DATE(CURRENT_DATE - 1)
        AND ft.total < 500
        GROUP BY t.truck_id, t.truck_name;
        """

    with conn.cursor() as cur:
        cur.execute(query)
        results = cur.fetchall()
    
    formatted_results = [
        {'truck_id':truck_id, 'truck_name':truck_name, 'mean_transaction_value':"{:.2f}".format(mean_transaction_value), 'median_transaction_value':"{:.2f}".format(median_transaction_value)}
        for truck_id, truck_name, mean_transaction_value, median_transaction_value in results
    ]

    return formatted_results


if __name__ == "__main__":

    load_dotenv()

    config = {}

    config["DB_PASSWORD"] = environ.get("DB_PASSWORD")
    config["DB_NAME"] = environ.get("DB_NAME")
    config["DB_USER"] = environ.get("DB_USER")
    config["DB_HOST"] = environ.get("DB_HOST")
    config["DB_PORT"] = environ.get("DEB_PORT")

    report_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    output_file = f'report_data_{report_date}.json'

    conn = connect(database=config["DB_NAME"],
                   user=config["DB_USER"],
                   password=config["DB_PASSWORD"],
                   host=config["DB_HOST"],
                   port=config["DB_PORT"])
    
    with conn.cursor() as cur:
        cur.execute("SET search_path TO sigma_annie_schema")

    total_transaction_value_for_all_trucks = total_transaction_value_all_trucks(conn)

    transactions_for_each_truck = transactions_per_truck(conn)

    transactions_for_each_truck = sorted(transactions_for_each_truck, key=lambda x: x['truck_id'])

    average_transaction_values_for_each_truck = mean_and_median_transaction_value_per_truck(conn)

    average_transaction_values_for_each_truck = sorted(average_transaction_values_for_each_truck, key=lambda x: x['truck_id'])
    
    daily_report_data = {
        'total_transaction_value_all_trucks': total_transaction_value_all_trucks(conn),
        'transaction-data_for_each_truck': transactions_for_each_truck,
        'avg_transaction_values_for_each_truck': average_transaction_values_for_each_truck
    }

    with open(output_file, 'w') as json_file:
        json.dump(daily_report_data, json_file, indent=4)

    print(daily_report_data)

    conn.commit()

    conn.close()