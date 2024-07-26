import os
import json
from statistics import mean
from django.http import JsonResponse
from django.conf import settings


def fetch_news_sentiment(tickers):
    response_dict = {}

    json_file_path = os.path.join(settings.BASE_DIR, 'data_model', 'user_sentiment.json')
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            for ticker in tickers:
                response_dict[ticker] = data['response_dict'].get(ticker, {})

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


def alpha_process_sentiment_data(request):
    tickers = request.GET.get('tickers', '')
    tickers_list = [ticker.strip() for ticker in tickers.split(',')]
    data = fetch_news_sentiment(tickers_list)

    sentiment_results = {}

    for ticker, ticker_data in data.items():
        sentiment_scores = [
            float(item['ticker_sentiment_score'])
            for feed in ticker_data.get('feed', [])
            for item in feed.get('ticker_sentiment', [])
            if item['ticker'] == ticker
        ]

        if sentiment_scores:
            mean_score = mean(sentiment_scores)
            sentiment_label = calculate_sentiment_label(mean_score)
            sentiment_results[ticker] = {
                'median_sentiment_score': mean_score,
                'sentiment': sentiment_label
            }

    return JsonResponse(sentiment_results)
