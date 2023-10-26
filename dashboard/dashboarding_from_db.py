from os import environ
from dotenv import load_dotenv
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from redshift_connector import connect


def dashboard_header():
    """
    Adds header to dashboard
    """
    st.title(""":violet[Food Truck Dashboard] :truck::burrito::oden:"""
             + """:cupcake::fishing_pole_and_fish::shaved_ice::sake:""")
    st.markdown("_now ad free with premium membership!_")


def headline_figures(transactions):
    """
    Adds headline figures to the dashboard
    """
    transactions['timestamp'] = pd.to_datetime(transactions['timestamp'])
    one_week_ago = pd.Timestamp.now() - pd.DateOffset(weeks=1)
    past_week_transactions = transactions[transactions['timestamp'] > one_week_ago]

    cols = st.columns(1)

    with cols[0]:
        st.metric("Total trucks", transactions["TruckID"].nunique(), delta=0.00)
        st.metric("Sales in the past week",
                  past_week_transactions["timestamp"].nunique(), delta=-0.01)


def transactions_per_truck(transactions):
    """
    Bar chart which displays how many transactions
    that each truck has
    """
    truck_id_name_mapping = {1: "1: Burrito Madness", 2: "2: Kings of Kebabs",
                             3: "3: Cupcakes by Michelle", 4: "4: Hartmann's Jellied Eels",
                             5: "5: Yoghurt Heaven", 6: "6: SuperSmoothie"}

    transactions['TruckID'] = transactions['TruckID'].map(truck_id_name_mapping)

    truck_id_counts = transactions['TruckID'].value_counts()

    plt.figure(figsize=(10,5))
    plt.bar(truck_id_counts.index, truck_id_counts.values,
            color=['#CDB4DB','#ffc8dd','#fad2e1','#ffafcc','#bde0fe','#a2d2ff'])
    plt.xlabel("Truck Name")
    plt.xticks(rotation=25)
    plt.ylabel("Count")
    plt.title("Sales Per Truck")

    st.pyplot()


def sales_by_hour(transactions):
    """
    Line chart showing the average sales
    for each hour of the day
    """
    transactions['hour'] = transactions['timestamp'].dt.hour
    average_sales_per_hour = transactions.groupby('hour')['total'].mean().reset_index()

    plt.figure(figsize=(10,5))
    plt.plot(average_sales_per_hour['hour'], average_sales_per_hour['total'],
             marker='o', color='#d0f4de')
    plt.xlabel("Hour of the Day")
    plt.ylabel("Average Sales")
    plt.title("Average Sales per Hour of the Day")

    st.pyplot()


def sales_by_hour_per_truck(transactions):
    """
    Shows how many sales each truck has,
    on average, for each hour of the day
    """
    transactions['hour'] = transactions['timestamp'].dt.hour
    average_sales_per_hour = transactions.groupby(['hour', 'TruckID'])['total'].mean().reset_index()

    plt.figure(figsize=(10, 5))

    truck_ids = average_sales_per_hour['TruckID'].unique()

    selected_trucks = st.multiselect('Select Trucks', average_sales_per_hour['TruckID'].unique())

    colours = ['#CDB4DB','#ffc8dd','#fad2e1','#ffafcc','#bde0fe','#a2d2ff']

    for i, truck_id in enumerate(selected_trucks):
        truck_data = average_sales_per_hour[average_sales_per_hour['TruckID'] == truck_id]
        plt.plot(truck_data['hour'], truck_data['total'],
                 marker='o', color=colours[i], label=f'Truck {truck_id}')

    plt.xlabel("Hour of the Day")
    plt.ylabel("Average Sales")
    plt.title("Average Sales per Hour of the Day by Truck")
    plt.legend(title="TruckID")

    st.pyplot(plt)


def total_income_per_day(transactions):
    """
    Displays a bar chart showing daily income
    """
    transactions['day'] = transactions['timestamp'].dt.day
    yearly_total_income = transactions.groupby('day')['total'].sum().reset_index()

    print(transactions['day'])

    plt.figure(figsize=(10, 5))
    plt.bar(yearly_total_income['day'], yearly_total_income['total'], color='#dfe7fd')
    plt.xlabel("Day")
    plt.ylabel("Total Income")
    plt.title("Total Income per Day")

    st.pyplot(plt)


def graph_for_sales_per_day(truck_data):
    """
    Displays sale totals for each truck,
    for each day of the week
    """
    truck_data['month'] = truck_data['timestamp'].dt.day_name()
    data = truck_data.groupby(["TruckID", "month"])["total"].sum().reset_index()
    fig, ax = plt.subplots()

    for id, group in data.groupby('TruckID'):
        ax.plot(group['month'], group['total'], label=id)

    ax.legend()
    ax.set_title("Sale totals for each truck each day of the week")
    plt.show()

    st.pyplot(fig)


def load_data(conn):
    """
    Fetches transaction data from
    the database
    """
    with conn.cursor() as cur:

        cur.execute("SELECT * FROM FACT_transactions")
        transactions_data = cur.fetch_dataframe()

        transactions_data.rename(
            columns={'truck_id':'TruckID','transaction_time':'timestamp'},
            inplace=True
            )

    return transactions_data


if __name__ == "__main__":

    load_dotenv()

    config = {}

    config["DB_PASSWORD"] = environ.get("DB_PASSWORD")
    config["DB_NAME"] = environ.get("DB_NAME")
    config["DB_USER"] = environ.get("DB_USER")
    config["DB_HOST"] = environ.get("DB_HOST")
    config["DB_PORT"] = environ.get("DEB_PORT")

    conn = connect(database=config["DB_NAME"],
                   user=config["DB_USER"],
                   password=config["DB_PASSWORD"],
                   host=config["DB_HOST"],
                   port=config["DB_PORT"])

    with conn.cursor() as cur:
        cur.execute("SET search_path TO sigma_annie_schema")

    st.set_option('deprecation.showPyplotGlobalUse', False)

    transactions = load_data(conn)

    dashboard_header()

    headline_figures(transactions)

    transactions_per_truck(transactions)

    sales_by_hour(transactions)

    sales_by_hour_per_truck(transactions)

    total_income_per_day(transactions)

    graph_for_sales_per_day(transactions)
