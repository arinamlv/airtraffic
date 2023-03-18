import streamlit as st
import pandas as pd

HOME_AIRPORTS = ('LGW', 'LIS', 'LYS')
PAIRED_AIRPORTS = ('FUE', 'AMS', 'ORY')

st.title('Traffic Forecaster')

with st.sidebar:
    home_airport = st.selectbox(
        'Home Airport', HOME_AIRPORTS)
    paired_airport = st.selectbox(
        'Paired Airport', PAIRED_AIRPORTS)
    forecast_date = st.date_input('Forecast start day')
    nb_days = st.slider('Days of forecast', 0, 30, 1)
    run_forecast = st.button('Forecast')
    
st.write('Home Airport selected', home_airport)
st.write('Paired Airport selected', paired_airport)
st.write('Days of forecast:', nb_days)
st.write('Date selected:', forecast_date)

#st.write(df.query('home_aiport = "{}"'.format(home_airport)).shape[0]