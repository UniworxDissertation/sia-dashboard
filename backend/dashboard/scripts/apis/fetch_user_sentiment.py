import os
import json
import time
import requests
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.conf import settings

from dashboard.scripts.constants import ALPHA_VANTAGE_API_KEY


# def fetch_news_sentiment(tickers):
#     # Path to the JSON file
#     json_file_path = os.path.join(settings.BASE_DIR, 'data_model', 'user_sentiment.json')
#     print(json_file_path)
#
#     # Check if the JSON file exists
#     if os.path.exists(json_file_path):
#         with open(json_file_path, 'r') as file:
#             data = json.load(file)
#             timestamp = datetime.fromtimestamp(data['timestamp'])
#
#             # Check if the file is older than 24 hours
#             if datetime.now() - timestamp < timedelta(hours=24):
#                 if all(ticker in data['response_dict'] for ticker in tickers):
#                     print("Using cached sentiment data.")
#                     return {ticker: data['response_dict'][ticker] for ticker in tickers}
#
#     # If the file doesn't exist or is older than 24 hours, fetch new data
#     response_dict = {}
#     for ticker in tickers:
#         url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
#         response = requests.get(url)
#         response_dict[ticker] = response.json()
#
#     # Save the response dictionary with a timestamp to the JSON file
#     data_to_save = {
#         'timestamp': time.time(),
#         'response_dict': response_dict
#     }
#     os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
#     with open(json_file_path, 'w') as file:
#         json.dump(data_to_save, file)
#
#     return response_dict


def fetch_news_sentiment(tickers):
    base_dir = os.path.join(settings.BASE_DIR, 'data_model', 'Sentiment JSONs')
    response_dict = {}

    for ticker in tickers:
        # Find all files in the directory that contain the ticker
        files = [f for f in os.listdir(base_dir) if ticker in f]

        for file_name in files:
            json_file_path = os.path.join(base_dir, file_name)
            if os.path.exists(json_file_path):
                with open(json_file_path, 'r') as file:
                    data = json.load(file)
                    response_dict[ticker] = data

    return response_dict
