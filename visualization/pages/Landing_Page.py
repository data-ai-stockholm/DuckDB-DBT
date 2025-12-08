import datetime
import streamlit as st
import duckdb
import pandas as pd
import shutil
import os

# Page layout settings
st.set_page_config(
    layout="wide"
)

# Creating the read-only database for visualization
write_db_path = "../transformation/weather_reports.db"
read_db_path = "../visualization/weather_reports_ro.db"

while not (os.path.exists(write_db_path)):
    st.warning("Waiting for the transformed database to be created...")
    st.sleep(5)

try:
    # Copy the file to the destination directory
    # If the destination is a directory, the file will be copied into it
    # with its original filename.
    shutil.copy(write_db_path, read_db_path)
    print(f"File '{write_db_path}' successfully copied to '{read_db_path}'.")
except FileNotFoundError:
    print(f"Error: Source file '{write_db_path}' not found.")
except Exception as e:
    print(f"An error occurred: {e}")

# LOAD DATA FOR FRONTEND USAGE
conn = duckdb.connect(database=read_db_path, read_only=True)

@st.cache_data
def load_weather_data(db_path: str, weather_date_range: tuple, station_name: str) -> pd.DataFrame:
    conn = duckdb.connect(database=db_path, read_only=True)

    start_date = weather_date_range[0].strftime("%Y-%m-%d")
    end_date = weather_date_range[1].strftime("%Y-%m-%d")

    query = f"""
        SELECT *
        FROM fact_observations
        WHERE TRUE
            AND DATE(observation_timestamp) BETWEEN '{start_date}' AND '{end_date}'
            AND station_name IN {station_name};
    """

    df = conn.execute(query).df()
    return df

@st.cache_data
def load_station_data(db_path: str) -> pd.DataFrame:
    conn = duckdb.connect(database=db_path, read_only=True)

    query = """
        SELECT
            DISTiNCT station_name,
        FROM fact_observations
        ORDER BY station_name;
    """

    df = conn.execute(query).df()
    return df

# STREAMLIT FRONTEND
st.header("Weather Reports Application")

date_range_filter_column, station_filter_column = st.columns(2)

# Date input for weather data filtering
today = datetime.datetime.now()
next_year = today.year + 1
nov_29 = datetime.date(today.year, 11, 29)
dec_31 = datetime.date(today.year, 12, 31)

with date_range_filter_column:
    weather_date_range = st.date_input(
        "Filter the date range for weather data:",
        (nov_29, datetime.date(today.year, 12, 31)),
        nov_29,
        dec_31,
        format="MM.DD.YYYY",
    )

with station_filter_column:
    selected_station = st.multiselect(
        "Pick the station:",
        load_station_data(read_db_path)['station_name'].tolist(),
        max_selections=1,
        accept_new_options=False,
        default='University of Miami' # Temporarily set a default station
    )

chart1, chart2 = st.columns(2)
chart3, chart4 = st.columns(2)
chart5, chart6 = st.columns(2)
chart7, chart8 = st.columns(2)
chart9, chart10 = st.columns(2)

try:
    weather_data_df = load_weather_data(read_db_path, weather_date_range, selected_station)
    if weather_data_df.empty:
        st.info("No records found in weather data table.")
    else:
        # st.dataframe(weather_data_df)
        with chart1:
            st.line_chart(data=weather_data_df, x='observation_timestamp', y='temperature_degC', x_label='datetime', y_label='Temperature (℃)', color='#ffaa00', width="stretch", height="content", use_container_width=None)
        with chart2:
            st.line_chart(data=weather_data_df, x='observation_timestamp', y='dewpoint_degC', x_label='datetime', y_label='Dew Point (℃)', color='#ffaa00', width="stretch", height="content", use_container_width=None)
        with chart3:
            st.line_chart(data=weather_data_df, x='observation_timestamp', y='wind_speed_kmh', x_label='datetime', y_label='Wind Speed (kmh)', color='#ffaa00', width="stretch", height="content", use_container_width=None)
        with chart4:
            st.line_chart(data=weather_data_df, x='observation_timestamp', y='wind_gust_kmh', x_label='datetime', y_label='Wind Gust (knh)', color='#ffaa00', width="stretch", height="content", use_container_width=None)
        with chart5:
            st.line_chart(data=weather_data_df, x='observation_timestamp', y='barometric_pressure_Pa', x_label='datetime', y_label='Barometric Pressure (Pa)', color='#ffaa00', width="stretch", height="content", use_container_width=None)
        with chart6:
            st.line_chart(data=weather_data_df, x='observation_timestamp', y='sea_level_pressure_Pa', x_label='datetime', y_label='Sea Level Pressure (Pa)', color='#ffaa00', width="stretch", height="content", use_container_width=None)
        with chart7:
            st.line_chart(data=weather_data_df, x='observation_timestamp', y='visibility_m', x_label='datetime', y_label='Visibility (m)', color='#ffaa00', width="stretch", height="content", use_container_width=None)
        with chart8:
            st.line_chart(data=weather_data_df, x='observation_timestamp', y='relative_humidity_percent', x_label='datetime', y_label='Relative Humidity %', color='#ffaa00', width="stretch", height="content", use_container_width=None)
        with chart9:
            st.line_chart(data=weather_data_df, x='observation_timestamp', y='wind_direction_deg', x_label='datetime', y_label='Wind Direction (℃)', color='#ffaa00', width="stretch", height="content", use_container_width=None)
        with chart10:
            st.line_chart(data=weather_data_df, x='observation_timestamp', y='precipitation_3h_mm', x_label='datetime', y_label='Relative Precipitation (mm)', color='#ffaa00', width="stretch", height="content", use_container_width=None)
except Exception as e:
    st.error(f"Failed to load weather data table: {e}")