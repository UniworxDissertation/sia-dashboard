import os
import json
import time
from datetime import datetime, timedelta
import requests
from django.conf import settings
from django.http import JsonResponse

ALPHA_VANTAGE_API_KEY = '3UD403K0HOLS40AD'  # Replace with your actual API key


def fetch_alpha_news_sentiment(tickers):
    # Path to the JSON file
    json_file_path = os.path.join(settings.BASE_DIR, 'data_model', 'user_sentiment.json')

    # Check if the JSON file exists
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            timestamp = datetime.fromtimestamp(data['timestamp'])

            # Check if the file is older than 24 hours
            if datetime.now() - timestamp < timedelta(hours=24):
                if all(ticker in data['response_dict'] for ticker in tickers):
                    print("Using cached sentiment data.")
                    return {ticker: data['response_dict'][ticker] for ticker in tickers}

    # If the file doesn't exist or is older than 24 hours, fetch new data
    response_dict = {}
    for ticker in tickers:
        url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&apikey={ALPHA_VANTAGE_API_KEY}&limit=1000"
        response = requests.get(url)
        response_dict[ticker] = response.json()

    # Save the response dictionary with a timestamp to the JSON file
    data_to_save = {
        'timestamp': time.time(),
        'response_dict': response_dict
    }
    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
    with open(json_file_path, 'w') as file:
        json.dump(data_to_save, file)

    return response_dict



