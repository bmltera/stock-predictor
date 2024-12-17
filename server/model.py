import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
from pandas.tseries.offsets import BDay

def predict(input_date, ticker="NVDA", n_past=30, n_future=5):
    # Convert input_date to a pandas Timestamp
    input_date = pd.to_datetime(input_date)
    
    # 60 day training data
    start_date = (input_date - pd.Timedelta(days=60)).strftime('%Y-%m-%d')
    end_date = input_date.strftime('%Y-%m-%d')

    # Yahoo Finance
    stock = yf.Ticker(ticker)
    data = stock.history(start=start_date, end=end_date)
    
    # Error check
    if len(data) < n_past:
        raise ValueError(f"Not enough data to get {n_past} past days. Only got {len(data)} days.")
    
    # Select the n_past days
    recent_data = data[['Open', 'High', 'Low', 'Close']].iloc[-n_past:]
    
    # Fit scalar
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_recent = scaler.fit_transform(recent_data)
    
    # Load the saved model
    model = load_model("nvda_lstm_model.keras")
    
    input_data = np.expand_dims(scaled_recent, axis=0)
    
    # Predict
    prediction = model.predict(input_data)
    prediction = prediction.reshape(n_future, 4)
    predicted_prices = scaler.inverse_transform(prediction)
    
    # Create a DataFrame
    start_pred_date = input_date + pd.offsets.BDay(1)
    pred_index = pd.date_range(start=start_pred_date, periods=n_future, freq='B')
    predicted_df = pd.DataFrame(predicted_prices, columns=['Open', 'High', 'Low', 'Close'], index=pred_index)
    
    return predicted_df


