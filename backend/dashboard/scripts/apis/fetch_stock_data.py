import pandas as pd
import os

from dashboard.scripts.constants import energy_companies, financial_companies

csv_path = (os.path.dirname(os.path.abspath(__file__)).replace('scripts\\apis',
                                                               'data_model/historical_financial_data.csv')
            .replace('\\dashboard', ''))


def read_csv():
    # Define the date parser
    date_parser = lambda x: pd.to_datetime(x, format='%Y-%m-%d')
    csv_Data = pd.read_csv(csv_path, index_col=0, parse_dates=True, date_parser=date_parser)
    # Reset the index to convert the date from index to a column
    csv_Data.reset_index(inplace=True)

    # Rename the date column
    csv_Data.rename(columns={'index': 'date'}, inplace=True)

    # Ensure data is sorted by date
    csv_Data = csv_Data.sort_values(by='date')

    return csv_Data


def fetch_energy_companies_data():
    csv_data = read_csv()
    energy_companies_data = pd.DataFrame()
    for company in energy_companies:
        company_data = csv_data[csv_data['symbol'] == company]
        energy_companies_data = pd.concat([energy_companies_data, company_data], ignore_index=True)
    return energy_companies_data


def fetch_financial_companies_data():
    csv_data = read_csv()
    financial_companies_data = pd.DataFrame()
    for company in financial_companies:
        company_data = csv_data[csv_data['symbol'] == company]
        financial_companies_data = pd.concat([financial_companies_data, company_data], ignore_index=True)
    return financial_companies_data
