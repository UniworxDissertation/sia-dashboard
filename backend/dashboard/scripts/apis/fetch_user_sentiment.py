import os
import json
from django.conf import settings


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
