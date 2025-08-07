import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Smart Energy Dashboard", layout="wide")
st.title("\U0001F50B Smart Energy Insights Dashboard")

# File uploader
uploaded_file = st.file_uploader("Upload your energy consumption CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, parse_dates=['Timestamp'])

    # Clean and extract time components
    df['Hour'] = df['Timestamp'].dt.hour
    df['Date'] = df['Timestamp'].dt.date
    df['Day'] = df['Timestamp'].dt.day_name()
    df['Week'] = df['Timestamp'].dt.isocalendar().week
    df['Month'] = df['Timestamp'].dt.month_name()

    st.subheader("Raw Data Preview")
    st.dataframe(df.head(10))

    # Sidebar filters
    st.sidebar.header("Filter Data")
    state_filter = st.sidebar.multiselect("Select State", df['State'].unique(), default=df['State'].unique())
    city_filter = st.sidebar.multiselect("Select City", df['City'].unique(), default=df['City'].unique())

    filtered_df = df[(df['State'].isin(state_filter)) & (df['City'].isin(city_filter))]

    st.markdown("---")
    st.subheader("Total Consumption Summary")
    total_kwh = filtered_df['Power_Consumption_kWh'].sum()
    avg_kwh = filtered_df['Power_Consumption_kWh'].mean()
    peak_hour = filtered_df.groupby('Hour')['Power_Consumption_kWh'].mean().idxmax()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Consumption (kWh)", f"{total_kwh:.2f}")
    col2.metric("Average Consumption (kWh)", f"{avg_kwh:.2f}")
    col3.metric("Peak Usage Hour", f"{peak_hour}:00")

    # Line Chart: Hourly Pattern
    st.subheader("Hourly Consumption Pattern")
    hourly = filtered_df.groupby('Hour')['Power_Consumption_kWh'].mean().reset_index()
    fig1 = px.line(hourly, x='Hour', y='Power_Consumption_kWh', markers=True,
                   title="Average Consumption by Hour")
    st.plotly_chart(fig1, use_container_width=True)

    # Bar Chart: Daily Usage
    st.subheader("Daily Consumption Trends")
    daily = filtered_df.groupby('Date')['Power_Consumption_kWh'].sum().reset_index()
    fig2 = px.bar(daily, x='Date', y='Power_Consumption_kWh',
                  title="Daily Total Consumption", labels={'Power_Consumption_kWh': 'kWh'})
    st.plotly_chart(fig2, use_container_width=True)

    # Pie Chart: Area-wise usage
    st.subheader("Area-wise Consumption Distribution")
    area_wise = filtered_df.groupby('Area')['Power_Consumption_kWh'].sum().reset_index()
    fig3 = px.pie(area_wise, values='Power_Consumption_kWh', names='Area',
                  title="Total Consumption by Area")
    st.plotly_chart(fig3, use_container_width=True)

    # Anomaly Detection
    st.markdown("---")
    st.subheader("\U0001F52E Anomaly Detection")
    threshold = filtered_df['Power_Consumption_kWh'].mean() + 3 * filtered_df['Power_Consumption_kWh'].std()
    anomalies = filtered_df[filtered_df['Power_Consumption_kWh'] > threshold]

    st.write(f"Detected {len(anomalies)} anomalies where consumption > 3 std deviations:")
    st.dataframe(anomalies[['Timestamp', 'State', 'City', 'Area', 'Power_Consumption_kWh']])

    fig4 = px.scatter(filtered_df, x='Timestamp', y='Power_Consumption_kWh',
                      color=filtered_df['Power_Consumption_kWh'] > threshold,
                      title="Power Consumption with Anomalies Highlighted",
                      labels={'color': 'Anomaly'})
    st.plotly_chart(fig4, use_container_width=True)

    # Smart Tips
    st.markdown("---")
    st.subheader("Smart Energy Tips")
    if peak_hour >= 18:
        st.info("\u26A1 High usage during evening hours. Recommend shifting appliance usage to late night or morning.")
    if avg_kwh > 2:
        st.info("\u2705 Consider using energy-efficient appliances to reduce average consumption.")
    if total_kwh > 500:
        st.warning("\u26A0 High overall consumption. Suggest energy audit in high-load areas.")
else:
    st.warning("Please upload a CSV file to begin analysis.")
