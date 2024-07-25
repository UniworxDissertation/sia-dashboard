import requests
import pandas as pd
from datetime import datetime

ALPHA_VANTAGE_API_KEY = '3UD403K0HOLS40AD'
energy_companies = ['XOM', 'CVX', 'NEE', 'BP', 'SHEL']
financial_companies = ['JPM', 'GS', 'BAC', 'MS', 'WFC']


# Code for retrieving the data from Alpha Vantage API and create a CSV

# Function to fetch financial data from Alpha Vantage using the free endpoint
def fetch_financial_data(api_key, symbol):
    url = (f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}'
           f'&outputsize=full')
    response = requests.get(url)
    data = response.json()
    if "Time Series (Daily)" in data:
        df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index")
        df.columns = ["open", "high", "low", "close", "volume"]
        df.index = pd.to_datetime(df.index)
        df = df.astype(float)
        df['symbol'] = symbol  # Add a column for the symbol
        return df
    else:
        print(f"Error fetching data for {symbol}: {data['Note'] if 'Note' in data else data}")
        return None


# Fetch data for all companies and store in a dictionary
def fetch_all_data(companies, api_key):
    all_data = []
    for company in companies:
        data = fetch_financial_data(api_key, company)
        if data is not None:
            all_data.append(data)
    return pd.concat(all_data)


# Fetch data for energy and financial companies
energy_data = fetch_all_data(energy_companies, ALPHA_VANTAGE_API_KEY)
financial_data = fetch_all_data(financial_companies, ALPHA_VANTAGE_API_KEY)

# Combine data from both sectors
combined_data = pd.concat([energy_data, financial_data])

# Filter data to include only the last 5 years
five_years_ago = datetime.now().date().replace(year=datetime.now().year - 5)
combined_data = combined_data[combined_data.index >= pd.to_datetime(five_years_ago)]

# Save combined data to CSV
combined_data.to_csv('historical_financial_data.csv', index=True)

print("Data has been successfully fetched and saved to 'historical_financial_data.csv'")
