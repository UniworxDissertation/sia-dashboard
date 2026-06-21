import os
import json
import numpy as np
import pandas as pd

from pathlib import Path
from datetime import datetime
from collections import defaultdict
from statistics import mean
from scipy.stats import pearsonr
from django.conf import settings
from django.http import JsonResponse
from dashboard.scripts.apis import fetch_stock_data
from dashboard.scripts.apis import sentiment_segregation

def fetch_sentiment_and_stock_data(ticker):
    base_dir = Path(settings.BASE_DIR) / "data_model" / "Sentiment JSONs"
    sentiment_data = []
    csv_data = fetch_stock_data.read_csv()
    stock_data = []
    files = [f for f in base_dir.iterdir() if ticker in f.name]

    for file_name in files:
        json_file_path = base_dir / file_name
        if json_file_path.exists():
            with open(json_file_path, 'r') as file:
                data = json.load(file)
                sentiment_data.extend(data.get('data', []))

    sentiment_dates = {datetime.strptime(item['Time'], '%Y-%m-%dT%H:%M:%S.%fZ').date() for item in sentiment_data}

    filtered_stock_data = csv_data[csv_data['date'].isin(sentiment_dates)]

    for _, row in filtered_stock_data.iterrows():
        if ticker in row['symbol']:
            stock_data.append({
                'date': row['date'].strftime('%Y-%m-%d'),
                'close': row['close']
            })

    # Group sentiment scores by date
    sentiment_by_date = defaultdict(list)
    for item in sentiment_data:
        date_str = datetime.strptime(item['Time'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')
        sentiment_by_date[date_str].append(item['Sentiment_Score'])

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


def fetch_aggregated_correlation(tickers):
    correlations = []

    for ticker in tickers:
        _, _, correlation, _ = fetch_sentiment_and_stock_data(ticker)
        if correlation is not None:
            correlations.append(correlation)

    overall_correlation = mean(correlations) if correlations else None
    return overall_correlation


def fetch_sentiment_and_stock_data_with_lag(ticker, max_lag=10):
    base_dir = Path(settings.BASE_DIR) / "data_model" / "Sentiment JSONs"

    if not base_dir.exists():
        raise FileNotFoundError(f"Sentiment JSON folder not found: {base_dir}")

    sentiment_data = []
    csv_data = fetch_stock_data.read_csv()

    # Read sentiment JSON files for this ticker
    files = [
        file_path
        for file_path in base_dir.iterdir()
        if file_path.is_file()
        and file_path.suffix.lower() == ".json"
        and ticker.upper() in file_path.stem.upper()
    ]

    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            sentiment_data.extend(data.get("data", []))

    if not sentiment_data:
        return [], [], {}, None, None, None

    # Convert sentiment timestamps safely
    parsed_sentiment_rows = []

    for item in sentiment_data:
        parsed_time = pd.to_datetime(
            item.get("Time"),
            errors="coerce",
            utc=True
        )

        if pd.isna(parsed_time):
            continue

        sentiment_score = pd.to_numeric(
            item.get("Sentiment_Score"),
            errors="coerce"
        )

        if pd.isna(sentiment_score):
            continue

        parsed_sentiment_rows.append({
            "date": parsed_time.date(),
            "Sentiment_Score": float(sentiment_score),
        })

    if not parsed_sentiment_rows:
        return [], [], {}, None, None, None

    sentiment_dates = {item["date"] for item in parsed_sentiment_rows}

    # Prepare stock data safely
    stock_df = csv_data.copy()
    stock_df["date"] = pd.to_datetime(stock_df["date"], errors="coerce").dt.date
    stock_df["symbol"] = stock_df["symbol"].astype(str).str.upper()
    stock_df["close"] = pd.to_numeric(stock_df["close"], errors="coerce")

    # Filter by exact ticker and matching sentiment dates
    ticker_stock_df = stock_df[
        (stock_df["symbol"] == ticker.upper()) &
        (stock_df["date"].isin(sentiment_dates))
    ].copy()

    ticker_stock_df = ticker_stock_df.dropna(subset=["date", "close"])
    ticker_stock_df = ticker_stock_df.sort_values("date")

    stock_data = [
        {
            "date": row["date"].strftime("%Y-%m-%d"),
            "close": row["close"],
        }
        for _, row in ticker_stock_df.iterrows()
    ]

    # Group sentiment scores by date
    sentiment_by_date = defaultdict(list)

    for item in parsed_sentiment_rows:
        sentiment_by_date[item["date"]].append(item["Sentiment_Score"])

    aggregated_sentiment_data = []

    for date_value, scores in sentiment_by_date.items():
        avg_score = mean(scores)

        aggregated_sentiment_data.append({
            "date": date_value.strftime("%Y-%m-%d"),
            "Sentiment_Score": avg_score,
            "Sentiment_Label": sentiment_segregation.calculate_sentiment_label(avg_score),
        })

    aggregated_sentiment_data = sorted(
        aggregated_sentiment_data,
        key=lambda x: x["date"]
    )

    # Align sentiment and stock data by sorted date
    sentiment_lookup = {
        item["date"]: item["Sentiment_Score"]
        for item in aggregated_sentiment_data
    }

    stock_lookup = {
        item["date"]: item["close"]
        for item in stock_data
    }

    common_dates = sorted(set(sentiment_lookup).intersection(stock_lookup))

    if len(common_dates) < 2:
        return aggregated_sentiment_data, stock_data, {}, None, None, None

    sentiment_scores = [sentiment_lookup[date] for date in common_dates]
    stock_prices = [stock_lookup[date] for date in common_dates]

    def calculate_lagged_correlation(lag):
        if lag > 0:
            lagged_sentiment_scores = sentiment_scores[:-lag]
            lagged_stock_prices = stock_prices[lag:]
        else:
            lagged_sentiment_scores = sentiment_scores
            lagged_stock_prices = stock_prices

        if len(lagged_sentiment_scores) < 2 or len(lagged_stock_prices) < 2:
            return None

        if np.std(lagged_sentiment_scores) == 0 or np.std(lagged_stock_prices) == 0:
            return None

        correlation, _ = pearsonr(lagged_sentiment_scores, lagged_stock_prices)

        if np.isnan(correlation):
            return None

        return float(correlation)

    correlations_by_lag = {}

    for lag in range(max_lag + 1):
        correlation = calculate_lagged_correlation(lag)

        if correlation is not None:
            correlations_by_lag[lag] = correlation

    if correlations_by_lag:
        # Use absolute value if you want strongest relationship, positive or negative.
        optimal_lag = max(correlations_by_lag, key=lambda lag: abs(correlations_by_lag[lag]))
        optimal_correlation = correlations_by_lag[optimal_lag]
    else:
        optimal_lag = None
        optimal_correlation = None

    # Volatility for the selected ticker only
    ticker_stock_for_volatility = stock_df[
        stock_df["symbol"] == ticker.upper()
    ].copy()

    ticker_stock_for_volatility = ticker_stock_for_volatility.sort_values("date")

    daily_returns = ticker_stock_for_volatility["close"].pct_change().dropna()
    volatility = float(daily_returns.std()) if not daily_returns.empty else None

    return (
        aggregated_sentiment_data,
        stock_data,
        correlations_by_lag,
        optimal_lag,
        optimal_correlation,
        volatility,
    )
