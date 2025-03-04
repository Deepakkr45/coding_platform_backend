import pandas as pd
import pytz
from statsmodels.tsa.arima.model import ARIMA
from flask import jsonify

def perform_prediction_with_timestamps(data, prediction_hours):
    try:
        if data is None or data.empty:
            raise ValueError("Insufficient data for prediction.")

        time_diffs = data.index.to_series().diff().dropna()

        model = ARIMA(data['value'], order=(2, 0, 1))
        model_fit = model.fit()

        forecast_steps = prediction_hours * 12
        if forecast_steps <= 0:
            raise ValueError("Invalid number of forecast steps.")
        
        forecast = model_fit.forecast(steps=forecast_steps)

        first_timestamp = data.index[0]
        last_timestamp = data.index[-1]
        start_date = last_timestamp + pd.Timedelta(days=1)
        start_time = first_timestamp.time()
        start_datetime = pd.Timestamp.combine(start_date.date(), start_time).tz_localize('UTC')
        
        frequency = time_diffs.iloc[0]
        timestamps = pd.date_range(start=start_datetime, periods=forecast_steps, freq='5T')

        ist = pytz.timezone('Asia/Kolkata')
        formatted_timestamps = [ts.tz_convert(ist).strftime('%A, %B %d, %Y, %I:%M:%S %p (IST)') for ts in timestamps]
        
        return forecast.round(2), formatted_timestamps
    except Exception as e:
        raise ValueError("Error during prediction: {}".format(str(e)))
