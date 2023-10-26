import json
import datetime
import redshift_connector
from redshift_connector import connect, Connection
from os import environ
from datetime import datetime, timedelta
from dotenv import dotenv_values, load_dotenv

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


def create_html_file(data, date):

    report_header = f"<h1><font color='#CDB4DB'>🚚Daily Report {date}🚚</font></h1>"

    total_transaction_value_section = f"""
    <h2>Total Transaction Value Across All Trucks</h2>
    <p>{data['total_transaction_value_all_trucks'][0]}</p>
    """

    transactions_section = f"""
    <h2>Transaction Data for Each Truck</h2>
    {''.join(f"<p>Truck ID: {entry['truck_id']}<br>Truck Name: {entry['truck_name']}<br>Total Transaction Value: {entry['total_transaction_value']}<br>Transaction Count: {entry['transaction_count']}</p>" for entry in data['transaction-data_for_each_truck'])}
    """

    average_transaction_section = f"""
    <h2>Average Transaction Values for Each Truck</h2>
    {''.join(f"<p>Truck ID: {entry['truck_id']}<br>Truck Name: {entry['truck_name']}<br>Mean Transaction Value: {entry['mean_transaction_value']}<br>Median Transaction Value: {entry['median_transaction_value']}</p>" for entry in data['avg_transaction_values_for_each_truck'])}
    """

    truck_divider = """<h2>🚚🚚🚚🚚🚚🚚🚚🚚🚚🚚🚚🚚🚚🚚🚚🚚🚚🚚🚚🚚🚚🚚</h2>"""

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Daily Report</title>
        <style>
            body {{
                font-family: sans-serif;
                font-size: 25px;
                color: #f296b3;
                background-image: url('https://img.freepik.com/premium-vector/cute-truck-car-seamless-pattern-kids-hand-drawn-automobile-background-transport-wallpaper_97843-5843.jpg');
                background-repeat: repeat;
            }}
            h1, h2, p {{
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div style="border: 50px solid #adcfff; border-top: 50px solid #adcfff; border-bottom: 50px solid #adcfff; padding: 30px;">
            {report_header}
            {total_transaction_value_section}
            {truck_divider}
            {transactions_section}
            {truck_divider}
            {average_transaction_section}
            {truck_divider}
    </body>
    </html>
    """

    return html_content


def lambda_handler(event, context):
    
    load_dotenv()

    config = {
        "DB_PASSWORD": environ.get("DB_PASSWORD"),
        "DB_NAME": environ.get("DB_NAME"),
        "DB_USER": environ.get("DB_USER"),
        "DB_HOST": environ.get("DB_HOST"),
        "DB_PORT": environ.get("DEB_PORT")
    }

    report_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    conn = connect(
        database=config["DB_NAME"],
        user=config["DB_USER"],
        password=config["DB_PASSWORD"],
        host=config["DB_HOST"],
        port=config["DB_PORT"]
    )

    with conn.cursor() as cur:
        cur.execute("SET search_path TO sigma_annie_schema")

    transactions_for_each_truck = transactions_per_truck(conn)
    transactions_for_each_truck = sorted(transactions_for_each_truck, key=lambda x: x['truck_id'])
    average_transaction_values_for_each_truck = mean_and_median_transaction_value_per_truck(conn)
    average_transaction_values_for_each_truck = sorted(average_transaction_values_for_each_truck, key=lambda x: x['truck_id'])
    
    daily_report_data = {
        'total_transaction_value_all_trucks': total_transaction_value_all_trucks(conn),
        'transaction-data_for_each_truck': transactions_for_each_truck,
        'avg_transaction_values_for_each_truck': average_transaction_values_for_each_truck
    }

    html_content = create_html_file(daily_report_data, report_date)

    conn.close()

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': html_content
    }