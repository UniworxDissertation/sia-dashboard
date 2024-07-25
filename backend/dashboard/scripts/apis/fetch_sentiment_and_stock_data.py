import os
import json
from datetime import datetime
from collections import defaultdict
from statistics import mean
from django.conf import settings
from dashboard.scripts.apis import fetch_stock_data
from dashboard.scripts.apis import sentiment_segregation



def fetch_sentiment_and_stock_data(ticker):
    base_dir = os.path.join(settings.BASE_DIR, 'data_model', 'Sentiment JSONs')
    sentiment_data = []
    csv_data = fetch_stock_data.read_csv()
    stock_data = []
    files = [f for f in os.listdir(base_dir) if ticker in f]

    for file_name in files:
        json_file_path = os.path.join(base_dir, file_name)
        if os.path.exists(json_file_path):
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

    return aggregated_sentiment_data, stock_data
