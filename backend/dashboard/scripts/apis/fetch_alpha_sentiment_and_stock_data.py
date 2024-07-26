import os
import json
from datetime import datetime
from collections import defaultdict
from statistics import mean
from scipy.stats import pearsonr
from django.conf import settings
from django.http import JsonResponse
from dashboard.scripts.apis import fetch_stock_data
from dashboard.scripts.apis import sentiment_segregation


def fetch_alpha_sentiment_and_stock_data(ticker):
    json_file_path = os.path.join(settings.BASE_DIR, 'data_model', 'user_sentiment.json')
    sentiment_data = []
    csv_data = fetch_stock_data.read_csv()
    stock_data = []

    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            ticker_data = data['response_dict'].get(ticker, {})
            sentiment_data = ticker_data.get('feed', [])

    sentiment_dates = {datetime.strptime(item['time_published'], '%Y%m%dT%H%M%S').date() for item in sentiment_data}

    filtered_stock_data = csv_data[(csv_data['date'].isin(sentiment_dates)) &
                                   (csv_data['symbol'] == ticker)]

    for _, row in filtered_stock_data.iterrows():
        stock_data.append({
            'date': row['date'].strftime('%Y-%m-%d'),
            'close': row['close']
        })

    # Group sentiment scores by date
    sentiment_by_date = defaultdict(list)
    for item in sentiment_data:
        date_str = datetime.strptime(item['time_published'], '%Y%m%dT%H%M%S').strftime('%Y-%m-%d')
        for ticker_sentiment in item['ticker_sentiment']:
            if ticker_sentiment['ticker'] == ticker:
                sentiment_by_date[date_str].append(float(ticker_sentiment['ticker_sentiment_score']))

    # Calculate the mean sentiment score for each date
    aggregated_sentiment_data = [{
        'date': date,
        'Sentiment_Score': mean(scores),
        'Sentiment_Label': sentiment_segregation.calculate_sentiment_label(mean(scores))
    } for date, scores in sentiment_by_date.items() if datetime.strptime(date, '%Y-%m-%d').date() in sentiment_dates]

    # Sort aggregated sentiment data by date
    aggregated_sentiment_data = sorted(aggregated_sentiment_data, key=lambda x: x['date'])

    # Ensure both sentiment and stock data are aligned by date
    sentiment_scores = []
    stock_prices = []
    dates = set([item['date'] for item in aggregated_sentiment_data]).intersection(
        set([item['date'] for item in stock_data])
    )

    for date in dates:
        sentiment_scores.append(
            next(item['Sentiment_Score'] for item in aggregated_sentiment_data if item['date'] == date))
        stock_prices.append(next(item['close'] for item in stock_data if item['date'] == date))

    # Calculate correlation
    correlation, p_value = pearsonr(sentiment_scores, stock_prices) if sentiment_scores and stock_prices else (
        None, None)

    # Compute volatility
    daily_returns = filtered_stock_data['close'].pct_change().dropna()
    volatility = daily_returns.std() if not daily_returns.empty else None

    return aggregated_sentiment_data, stock_data, correlation, volatility


def sentiment_and_stock_data_view(request):
    ticker = request.GET.get('ticker', '').upper()
    if not ticker:
        return JsonResponse({'error': 'No ticker provided'}, status=400)

    sentiment_data, stock_data, correlation, volatility = fetch_alpha_sentiment_and_stock_data(ticker)

    return JsonResponse({
        'sentimentData': sentiment_data,
        'stockData': stock_data,
        'correlation': correlation,
        'volatility': volatility
    })
