import os
import time
from pathlib import Path
from datetime import datetime

import requests
import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand
from commands.user_sentiment_data_collection import fetch_news_sentiment
from dashboard.scripts.constants import energy_companies, financial_companies

from dashboard.scripts.constants import ALPHA_VANTAGE_API_KEY, energy_companies, financial_companies


class Command(BaseCommand):
    help = "Fetch Alpha Vantage financial and fundamental data and save CSV files."

    def handle(self, *args, **options):
        api_key = ALPHA_VANTAGE_API_KEY

        if not api_key:
            raise ValueError("ALPHA_VANTAGE_API_KEY is missing from environment/settings.")

        output_dir = Path(os.environ.get("DATA_OUTPUT_DIR", Path(settings.BASE_DIR) / "data_model"))
        output_dir.mkdir(parents=True, exist_ok=True)

        self.stdout.write("Starting daily financial data fetch...")

        energy_data = self.fetch_all_data(energy_companies, api_key, self.fetch_financial_data)
        financial_data = self.fetch_all_data(financial_companies, api_key, self.fetch_financial_data)

        combined_data = pd.concat([energy_data, financial_data])

        five_years_ago = pd.Timestamp.today().normalize() - pd.DateOffset(years=5)
        combined_data = combined_data[combined_data.index >= five_years_ago]

        historical_path = output_dir / "historical_financial_data.csv"
        combined_data.to_csv(historical_path, index=True)

        energy_fundamentals = self.fetch_all_data(energy_companies, api_key, self.fetch_fundamental_data)
        financial_fundamentals = self.fetch_all_data(financial_companies, api_key, self.fetch_fundamental_data)

        all_fundamentals = pd.concat([energy_fundamentals, financial_fundamentals])

        fundamentals_path = output_dir / "fundamental_data.csv"
        all_fundamentals.to_csv(fundamentals_path, index=False)

        combined_data_reset = combined_data.reset_index()
        all_fundamentals_reset = all_fundamentals.reset_index()

        final_data = pd.merge(
            combined_data_reset,
            all_fundamentals_reset,
            how="left",
            left_on="symbol",
            right_on="Symbol",
        )

        merged_path = output_dir / "merged_financial_data.csv"
        final_data.to_csv(merged_path, index=False)

        # Run News Sentiment Data Collection
        tickers = energy_companies + financial_companies
        fetch_news_sentiment(tickers)

        self.stdout.write(self.style.SUCCESS("Data has been successfully fetched and saved."))

    def fetch_financial_data(self, api_key, symbol):
        url = (
            "https://www.alphavantage.co/query"
            f"?function=TIME_SERIES_DAILY&symbol={symbol}"
            f"&apikey={api_key}&outputsize=full"
        )

        response = requests.get(url, timeout=60)
        response.raise_for_status()
        data = response.json()

        if "Time Series (Daily)" not in data:
            self.stdout.write(self.style.WARNING(f"Error fetching daily data for {symbol}: {data}"))
            return None

        df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index")
        df.columns = ["open", "high", "low", "close", "volume"]
        df.index = pd.to_datetime(df.index)
        df = df.astype(float)
        df["symbol"] = symbol

        return df

    def fetch_fundamental_data(self, api_key, symbol):
        url = (
            "https://www.alphavantage.co/query"
            f"?function=OVERVIEW&symbol={symbol}"
            f"&apikey={api_key}"
        )

        response = requests.get(url, timeout=60)
        response.raise_for_status()
        data = response.json()

        required_fields = [
            "Symbol", "MarketCapitalization", "PERatio", "PEGRatio", "BookValue",
            "DividendPerShare", "DividendYield", "EPS", "RevenuePerShareTTM",
            "ProfitMargin", "OperatingMarginTTM", "ReturnOnAssetsTTM",
            "ReturnOnEquityTTM", "RevenueTTM", "GrossProfitTTM", "DilutedEPSTTM",
            "QuarterlyEarningsGrowthYOY", "QuarterlyRevenueGrowthYOY",
            "AnalystTargetPrice", "TrailingPE", "ForwardPE", "PriceToSalesRatioTTM",
            "PriceToBookRatio", "EVToRevenue", "EVToEBITDA", "Beta", "52WeekHigh",
            "52WeekLow", "50DayMovingAverage", "200DayMovingAverage",
        ]

        if not data or not all(field in data for field in required_fields):
            self.stdout.write(self.style.WARNING(f"Error fetching fundamentals for {symbol}: {data}"))
            return None

        return pd.Series({field: data.get(field) for field in required_fields}, name=symbol)

    def fetch_all_data(self, companies, api_key, data_func):
        all_data = []

        for company in companies:
            data = data_func(api_key, company)

            if data is not None:
                all_data.append(data)

            # Alpha Vantage free tier is limited, so avoid hammering the API.
            time.sleep(15)

        if not all_data:
            raise ValueError("No data was fetched from Alpha Vantage.")

        if isinstance(all_data[0], pd.Series):
            return pd.concat(all_data, axis=1).T

        return pd.concat(all_data)
    
