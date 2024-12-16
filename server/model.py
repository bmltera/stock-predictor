import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
from pandas.tseries.offsets import BDay

def predict(input_date, ticker="NVDA", n_past=30, n_future=5):
    """
    Load the trained model, fetch the last 30 days of data up to the given date,
    predict the next 5 days of stock prices, and return them as a DataFrame.
    
    :param input_date: The end date (string, 'YYYY-MM-DD') up to which we consider historical data.
    :param ticker: The stock ticker symbol, default is "NVDA".
    :param n_past: Number of past days to use for prediction, default is 30.
    :param n_future: Number of future days to predict, default is 5.
    :return: A DataFrame with the predicted prices (Open, High, Low, Close).
    """
    
    # Convert input_date to a pandas Timestamp
    input_date = pd.to_datetime(input_date)
    
    # We will fetch a bit more than 30 days to ensure we get 30 trading days 
    # (in case there are weekends/holidays). Let's fetch the past 60 days.
    start_date = (input_date - pd.Timedelta(days=60)).strftime('%Y-%m-%d')
    end_date = input_date.strftime('%Y-%m-%d')

    # Fetch last 60 days of historical data from Yahoo Finance, then select last 30 trading days
    stock = yf.Ticker(ticker)
    data = stock.history(start=start_date, end=end_date)
    
    # If there's not enough data, return an empty DataFrame or raise an error
    if len(data) < n_past:
        raise ValueError(f"Not enough data to get {n_past} past days. Only got {len(data)} days.")
    
    # Select only the last n_past days
    recent_data = data[['Open', 'High', 'Low', 'Close']].iloc[-n_past:]
    
    # Fit a new scaler on these 30 days (Note: This won't be identical to training-time scaling)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_recent = scaler.fit_transform(recent_data)
    
    # Load the saved model
    model = load_model("nvda_lstm_model.keras")
    
    # Prepare input data for prediction
    input_data = np.expand_dims(scaled_recent, axis=0)
    
    # Predict
    prediction = model.predict(input_data)
    # Reshape predictions to (n_future, 4)
    prediction = prediction.reshape(n_future, 4)
    
    # Inverse transform predictions
    predicted_prices = scaler.inverse_transform(prediction)
    
    # Create a DataFrame with predicted prices
    # Predictions start from the next trading day after input_date.
    # We'll assume consecutive business days for the next 5 days.
    start_pred_date = input_date + pd.offsets.BDay(1)
    pred_index = pd.date_range(start=start_pred_date, periods=n_future, freq='B')
    predicted_df = pd.DataFrame(predicted_prices, columns=['Open', 'High', 'Low', 'Close'], index=pred_index)
    
    return predicted_df

def actual_from_date(input_date, ticker="NVDA", n_future=5):
    """
    Fetch the actual next 5 business days of data from Yahoo Finance after the given date.
    
    :param input_date: The end date (string, 'YYYY-MM-DD') up to which we consider historical data.
    :param ticker: The stock ticker symbol, default is "NVDA".
    :param n_future: Number of future days to fetch, default is 5.
    :return: A DataFrame with the actual prices (Open, High, Low, Close) for the next n_future trading days.
    """
    # Convert input_date to a pandas Timestamp
    input_date = pd.to_datetime(input_date)
    
    # Calculate the date range for the next 5 business days
    start_pred_date = input_date + BDay(1)
    pred_index = pd.date_range(start=start_pred_date, periods=n_future, freq='B')
    
    # Fetch data from Yahoo Finance to cover this range
    # We'll fetch a bit more than needed to ensure we capture all 5 trading days
    end_fetch_date = (pred_index[-1] + BDay(1)).strftime('%Y-%m-%d')
    start_fetch_date = pred_index[0].strftime('%Y-%m-%d')
    
    stock = yf.Ticker(ticker)
    future_data = stock.history(start=start_fetch_date, end=end_fetch_date)
    # Filter only the dates we need
    future_data = future_data[['Open', 'High', 'Low', 'Close']]
    # Format the index to YYYY-MM-DD
    future_data.index = future_data.index.strftime('%Y-%m-%d')
    # Print the actual prices
    return future_data

# Example usage:
test_date = "2024-8-03"
predicted_df = predict(test_date)
actual_df = actual_from_date(test_date)
print("Predicted Prices:")
print(predicted_df)
print("\nActual Prices:")
print(actual_df)



