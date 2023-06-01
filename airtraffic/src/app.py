import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly
import datetime
from prophet import Prophet
import plotly.offline as pyoff
import plotly.graph_objs as go
from plotly.subplots import make_subplots

traffic_df = pd.read_parquet("C:/Users/terso/Documents/Magistère ingénieur économiste/MAG3/Mignot/traffic_10lines.parquet")

HOME_AIRPORTS = traffic_df["home_airport"].unique().tolist()
PAIRED_AIRPORTS = traffic_df["paired_airport"].unique().tolist()

st.title('Traffic Forecaster')

with st.sidebar:
    home_airport = st.selectbox(
        'Home Airport', HOME_AIRPORTS)
    paired_airport = st.selectbox(
        'Paired Airport', PAIRED_AIRPORTS)
    run_forecast = st.button('Forecast')
    
st.write("Please select a correct route (see table below)")

data = [
    ('LGW', 'BCN'),
    ('LGW', 'AMS'),
    ('LIS', 'ORY'),
    ('LIS', 'OPO'),
    ('SSA', 'GRU'),
    ('NTE', 'FUE'),
    ('LYS', 'PIS'),
    ('PNH', 'NGB'),
    ('POP', 'JFK'),
    ('SCL', 'LHR')
]


df = pd.DataFrame(data, columns=['Home airport', 'Paired airport'])

st.table(df)

    
st.write('Home Airport selected:', home_airport)
st.write('Paired Airport selected:', paired_airport)

def generate_route_df(traffic_df, homeAirport, pairedAirport):
    _df = (traffic_df
           .query('home_airport == "{home}" and paired_airport == "{paired}"'.format(home=homeAirport, paired=pairedAirport))
           .groupby(['home_airport', 'paired_airport', 'date'])
           .agg(pax_total=('pax', 'sum'))
           .reset_index()
           )
    return _df

def run_prophet_forecast(traffic_df, homeAirport, pairedAirport, forecast_periods):
    route_df = generate_route_df(traffic_df, homeAirport, pairedAirport).rename(columns={'date': 'ds', 'pax_total': 'y'})

    baseline_model = Prophet()
    baseline_model.fit(route_df)

    future_df = baseline_model.make_future_dataframe(periods=forecast_periods)
    forecast_df = baseline_model.predict(future_df)

    return forecast_df

forecast_result = run_prophet_forecast(traffic_df, "LGW", "BCN", 15)

def draw_ts_multiple(df, v1, v2=None, prediction=None, date='date', secondary_y=True, covid_zone=False, display=True):
    if isinstance(v1, str):
        variables = [(v1, 'Actual')]
    else:
        variables = [(v, 'V1.{}'.format(i)) for i, v in enumerate(v1)]
    title = '<br>'.join([n + ': ' + v for v, n in variables]) + ('<br>V2: ' + v2) if v2 else '<br>'.join(
        [v + ': ' + n for v, n in variables])
    layout = dict(
        title=title,
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label='1m',
                         step='month',
                         stepmode='backward'),
                    dict(count=6,
                         label='6m',
                         step='month',
                         stepmode='backward'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type='date'
        )
    )
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.update_layout(layout)
    for v, name in variables:
        fig.add_trace(go.Scatter(x=df[date], y=df[v], name=name), secondary_y=False)
    if v2:
        fig.add_trace(go.Scatter(x=df[date], y=df[v2], name='V2'), secondary_y=secondary_y)
        fig['layout']['yaxis2']['showgrid'] = False
        fig.update_yaxes(rangemode='tozero')
        fig.update_layout(margin=dict(t=125 + 30 * (len(variables) - 1)))
    if prediction:
        fig.add_trace(go.Scatter(x=forecast_result["ds"], y=forecast_result["yhat"], name='Prediction', line={'dash': 'dot'}), secondary_y=False)

    if covid_zone:
        fig.add_vrect(
            x0=pd.Timestamp("2020-03-01"), x1=pd.Timestamp("2022-01-01"),
            fillcolor="Gray", opacity=0.5,
            layer="below", line_width=0,
        )
    if display:
        st.plotly_chart(fig)
    return fig


if run_forecast:
    st.title("Forecast traffic for selected route using prophet (15 days)")
    draw_ts_multiple(
    (traffic_df
     .query('home_airport == "LGW" and paired_airport == "BCN"')
     .groupby(['home_airport', 'paired_airport', 'date'])
     .agg(pax_total=('pax', 'sum'))
     .reset_index()
    ),
    'pax_total',
    covid_zone=True,
    prediction=True)


