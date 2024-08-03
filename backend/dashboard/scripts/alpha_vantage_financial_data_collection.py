import requests
import pandas as pd
from datetime import datetime

ALPHA_VANTAGE_API_KEY = '3UD403K0HOLS40AD'
energy_companies = ['XOM', 'CVX', 'NEE', 'BP', 'SHEL']
financial_companies = ['JPM', 'GS', 'BAC', 'MS', 'WFC']


# Function to fetch daily time series data
def fetch_financial_data(api_key, symbol):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}&outputsize=full'
    response = requests.get(url)
    data = response.json()

    if "Time Series (Daily)" in data:
        df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index")
        df.columns = ["open", "high", "low", "close", "volume"]
        df.index = pd.to_datetime(df.index)
        df = df.astype(float)
        df['symbol'] = symbol
        return df
    else:
        print(f"Error fetching data for {symbol}: {data['Note'] if 'Note' in data else data}")
        return None


# Function to fetch additional fundamental data
def fetch_fundamental_data(api_key, symbol):
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}'
    response = requests.get(url)
    data = response.json()

    if data and not isinstance(data, dict):
        return pd.Series(data, name=symbol)
    else:
        print(f"Error fetching fundamental data for {symbol}: {data['Note'] if 'Note' in data else data}")
        return None


# Fetch data for all companies and store in a dictionary
def fetch_all_data(companies, api_key, data_func):
    all_data = []
    for company in companies:
        data = data_func(api_key, company)
        if data is not None:
            all_data.append(data)
    if isinstance(all_data[0], pd.Series):
        return pd.concat(all_data, axis=1).T
    else:
        return pd.concat(all_data)


# Fetch all data for energy and financial
energy_data = fetch_all_data(energy_companies, ALPHA_VANTAGE_API_KEY, fetch_financial_data)
financial_data = fetch_all_data(financial_companies, ALPHA_VANTAGE_API_KEY, fetch_financial_data)
# Combine data from both sectors
combined_data = pd.concat([energy_data, financial_data])

# Filter data to include only the last 5 years
five_years_ago = datetime.now().date().replace(year=datetime.now().year - 5)
combined_data = combined_data[combined_data.index >= pd.to_datetime(five_years_ago)]

# Save combined data to CSV
combined_data.to_csv('historical_financial_data.csv', index=True)

# Fetch all fundamental data
energy_fundamentals = fetch_all_data(energy_companies, ALPHA_VANTAGE_API_KEY, fetch_fundamental_data)
financial_fundamentals = fetch_all_data(financial_companies, ALPHA_VANTAGE_API_KEY, fetch_fundamental_data)
# Combine data from both sectors
all_fundamentals = pd.concat([energy_fundamentals, financial_fundamentals])

# Save fundamental data
all_fundamentals.to_csv('fundamental_data.csv')

print("Data has been successfully fetched and saved to CSV files!")
