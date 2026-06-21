import json
import time
import requests
from pathlib import Path
from datetime import datetime, timedelta

from django.conf import settings
from dashboard.scripts.constants import ALPHA_VANTAGE_API_KEY


def fetch_news_sentiment(tickers):
    if not ALPHA_VANTAGE_API_KEY:
        raise ValueError("ALPHA_VANTAGE_API_KEY is missing from environment variables.")

    json_file_path = Path(settings.BASE_DIR) / "dataset" / "user_sentiment.json"
    json_file_path.parent.mkdir(parents=True, exist_ok=True)

    if json_file_path.exists():
        with open(json_file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        timestamp = datetime.fromtimestamp(data.get("timestamp", 0))

        if datetime.now() - timestamp < timedelta(hours=24):
            response_dict = data.get("response_dict", {})

            if all(ticker in response_dict for ticker in tickers):
                print("Using cached sentiment data.")
                return {ticker: response_dict[ticker] for ticker in tickers}

    response_dict = {}

    for ticker in tickers:
        url = (
            "https://www.alphavantage.co/query"
            f"?function=NEWS_SENTIMENT&tickers={ticker}"
            f"&apikey={ALPHA_VANTAGE_API_KEY}"
        )

        response = requests.get(url, timeout=60)
        response.raise_for_status()

        response_dict[ticker] = response.json()

        # Avoid hitting Alpha Vantage rate limits too aggressively.
        time.sleep(15)

    data_to_save = {
        "timestamp": time.time(),
        "response_dict": response_dict,
    }

    with open(json_file_path, "w", encoding="utf-8") as file:
        json.dump(data_to_save, file)

    return response_dict