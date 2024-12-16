from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import threading
import time
import requests
from datetime import datetime  # This is more common
from model import predict as model_predict  # Renamed on import


app = Flask(__name__)
CORS(app)

def keep_alive():
    while True:
        try:
            requests.get('https://stock-predictor-backend.onrender.com') 
            #requests.get('http://localhost:8000') 
            print(f"Keep-alive request sent: {time.strftime('%Y-%m-%d %H:%M:%S')}.")
        except Exception as e:
            print(f"Error sending keep-alive request: {e}")
        time.sleep(random.uniform(300, 600))

thread = threading.Thread(target=keep_alive)
thread.daemon = True 
thread.start()


def transform_predictions(predictions):
    # predictions is a list of dicts, each with keys: Close, High, Low, Open, date

    # Extract needed values
    closes = [p['Close'] for p in predictions]
    highs = [p['High'] for p in predictions]
    lows = [p['Low'] for p in predictions]

    # Compute avg, high, low
    avg_close = sum(closes) / len(closes) if closes else 0
    overall_high = max(highs) if highs else 0
    overall_low = min(lows) if lows else 0

    # Determine strategy for each day
    strategy_list = []
    for p in predictions:
        # Simple logic:
        # If Close > Open -> BULL
        # If Close < Open -> BEAR
        # Else -> IDLE
        if p['Close'] > p['Open']:
            strat = "BULL"
        elif p['Close'] < p['Open']:
            strat = "BEAR"
        else:
            strat = "IDLE"
        strategy_list.append([p['date'], strat])

    # Round values to 2 decimal places or as needed
    result = {
        "avg": round(avg_close, 2),
        "high": round(overall_high, 2),
        "low": round(overall_low, 2),
        "strategy": strategy_list
    }
    return result

@app.route('/predict', methods=['GET'])
def get_prediction():


    # date = request.args.get('date')
    
    # if not date:
    #     return jsonify({"error": "Date parameter is required"}), 400

    # high = round(random.uniform(10, 200), 2)
    # low = round(random.uniform(10, high), 2)
    # avg = round((high + low) / 2, 2)

    # strategies = ["BULL", "BEAR", "BULL", "BULL", "BEAR"]
    # trading_strategy = [(date, strategy) for strategy in strategies]

    # response = {
    #     "high": high,
    #     "low": low,
    #     "avg": avg,
    #     "strategy": trading_strategy
    # }
    # return jsonify(response)

    try:
        # Get input date from query parameters
        input_date = request.args.get('date')        
        if not input_date:
            return jsonify({'error': 'Date parameter is required'}), 400
            
        # Validate input date
        try:
            datetime.strptime(input_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
            
        # Get predictions
        predicted_df = model_predict(input_date)  # Using renamed import
        
        # Convert predictions to dictionary format
        predictions = predicted_df.to_dict(orient='records')
        
        # Format dates in the response
        for i, pred in enumerate(predictions):
            pred['date'] = predicted_df.index[i].strftime('%Y-%m-%d')
        
        transformed = transform_predictions(predictions)

        response = {
            "high": transformed["high"],
            "low": transformed["low"],
            "avg": transformed["avg"],
            "strategy": transformed["strategy"]
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True, port=8000)