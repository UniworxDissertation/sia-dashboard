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


# New function: Calculate aggregated correlation for multiple tickers
def fetch_aggregated_correlation(tickers):
    correlations = []

    for ticker in tickers:
        _, _, correlation, _ = fetch_alpha_sentiment_and_stock_data(ticker)
        if correlation is not None:
            correlations.append(correlation)

    overall_correlation = mean(correlations) if correlations else None
    return overall_correlation


# New function: Calculate lagged correlation for a specific ticker
def fetch_alpha_sentiment_and_stock_data_with_lag(ticker, max_lag=10):
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

    # Function to calculate correlation with lag
    def calculate_lagged_correlation(lag):
        lagged_sentiment_scores = sentiment_scores[:-lag] if lag > 0 else sentiment_scores
        lagged_stock_prices = stock_prices[lag:] if lag > 0 else stock_prices
        if len(lagged_sentiment_scores) > 1 and len(lagged_stock_prices) > 1:
            correlation, _ = pearsonr(lagged_sentiment_scores, lagged_stock_prices)
            return correlation
        return None

    # Calculate correlation for each lag (from 0 to max_lag days)
    correlations_by_lag = {lag: correlation for lag in range(max_lag + 1)
                           if (correlation := calculate_lagged_correlation(lag)) is not None}

    # Find the optimal lag
    optimal_lag = max(correlations_by_lag, key=correlations_by_lag.get)
    optimal_correlation = correlations_by_lag[optimal_lag]

    # Compute volatility
    daily_returns = filtered_stock_data['close'].pct_change().dropna()
    volatility = daily_returns.std() if not daily_returns.empty else None

    return aggregated_sentiment_data, stock_data, correlations_by_lag, optimal_lag, optimal_correlation, volatility


# Existing endpoint for basic sentiment and stock data
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


# New endpoint for lagged correlation analysis
def sentiment_and_stock_data_with_lag_view(request):
    ticker = request.GET.get('ticker', '').upper()
    max_lag = int(request.GET.get('max_lag', 10))  # Default to 10-day lag if not provided

    if not ticker:
        return JsonResponse({'error': 'No ticker provided'}, status=400)

    sentiment_data, stock_data, correlations_by_lag, optimal_lag, optimal_correlation, volatility = \
        fetch_alpha_sentiment_and_stock_data_with_lag(ticker, max_lag)

    return JsonResponse({
        'sentimentData': sentiment_data,
        'stockData': stock_data,
        'correlationsByLag': correlations_by_lag,
        'optimalLag': optimal_lag,
        'optimalCorrelation': optimal_correlation,
        'volatility': volatility
    })
