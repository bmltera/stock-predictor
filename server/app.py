from flask import Flask, request, jsonify
import random
import threading
import time
import requests

app = Flask(__name__)

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


@app.route('/predict', methods=['GET'])
def predict():
    date = request.args.get('date')
    
    if not date:
        return jsonify({"error": "Date parameter is required"}), 400

    high = round(random.uniform(10, 200), 2)
    low = round(random.uniform(10, high), 2)
    avg = round((high + low) / 2, 2)

    strategies = ["BULL", "BEAR", "BULL", "BULL", "BEAR"]
    trading_strategy = [(date, strategy) for strategy in strategies]

    response = {
        "high": high,
        "low": low,
        "avg": avg,
        "strategy": trading_strategy
    }

    return jsonify(response)


@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True, port=8000)