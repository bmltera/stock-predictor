from flask import Flask, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/predict', methods=['GET'])
def predict():
    # Get the date from the query parameters
    date = request.args.get('date')
    
    if not date:
        return jsonify({"error": "Date parameter is required"}), 400


    # SAMPLE DATA
    high = round(random.uniform(10, 200), 2)  # Random high price 
    low = round(random.uniform(10, high), 2)  # Random low price 
    avg = round((high + low) / 2, 2)       

    strategies = ["BULL", "BEAR", "BULL", "BULL", "TEST"]
    
    trading_strategy = [(date, strategy) for strategy in strategies]

    # Create the response object
    response = {
        "high": high,
        "low": low,
        "avg": avg,
        "strategy": trading_strategy
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(host ='0.0.0.0', debug=True, port=8000)