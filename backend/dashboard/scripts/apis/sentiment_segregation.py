import os
import json
import time
import requests
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.conf import settings
from statistics import mean

ALPHA_VANTAGE_API_KEY = 'your_alpha_vantage_api_key'  # Replace with your actual API key


def fetch_news_sentiment(tickers):
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
        url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
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


def calculate_sentiment_label(mean_score):
    if mean_score <= -0.35:
        return "Bearish"
    elif -0.35 < mean_score <= -0.15:
        return "Somewhat-Bearish"
    elif -0.15 < mean_score < 0.15:
        return "Neutral"
    elif 0.15 <= mean_score < 0.35:
        return "Somewhat-Bullish"
    else:
        return "Bullish"


def process_sentiment_data(request):
    tickers = request.GET.get('tickers', '')
    tickers_list = [ticker.strip() for ticker in tickers.split(',')]
    data = fetch_news_sentiment(tickers_list)

    sentiment_results = {}

    for ticker, ticker_data in data.items():
        sentiment_scores = [
            float(sentiment['ticker_sentiment_score'])
            for feed in ticker_data.get('feed', [])
            for sentiment in feed.get('ticker_sentiment', [])
            if sentiment['ticker'] == ticker
        ]

        if sentiment_scores:
            mean_score = mean(sentiment_scores)
            sentiment_label = calculate_sentiment_label(mean_score)
            sentiment_results[ticker] = {
                'mean_sentiment_score': mean_score,
                'sentiment': sentiment_label
            }

    return JsonResponse(sentiment_results)

