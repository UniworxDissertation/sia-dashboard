import os
import json
from statistics import mean
from django.http import JsonResponse
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


def calculate_sentiment_label(score):
    if score <= -0.35:
        return "Bearish"
    elif -0.35 < score <= -0.15:
        return "Somewhat-Bearish"
    elif -0.15 < score < 0.15:
        return "Neutral"
    elif 0.15 <= score < 0.35:
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
            float(feed['Sentiment_Score'])
            for feed in ticker_data.get('data', [])
        ]

        if sentiment_scores:
            mean_score = mean(sentiment_scores)
            sentiment_label = calculate_sentiment_label(mean_score)
            sentiment_results[ticker] = {
                'median_sentiment_score': mean_score,
                'sentiment': sentiment_label
            }

    return JsonResponse(sentiment_results)
