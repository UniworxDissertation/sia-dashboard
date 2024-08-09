import pandas as pd
from django.http import JsonResponse
from django.conf import settings
import os
from scipy.stats import pearsonr

from dashboard.scripts.apis import fetch_stock_data


# Mapping of ESG ratings to numerical values
ESG_MAPPING = {
    "AAA": 7,
    "AA": 6,
    "A": 5,
    "BBB": 4,
    "BB": 3,
    "B": 2,
    "CCC": 1
}


def load_esg_data(file_path):
    esg_data = pd.read_csv(file_path)
    esg_data.fillna(esg_data.mode().iloc[0], inplace=True)
    for year in esg_data.columns[1:]:
        esg_data[year] = esg_data[year].map(ESG_MAPPING)
    esg_dict = esg_data.set_index('symbol').T.to_dict(orient='dict')
    return esg_dict


def load_stock_price_changes():
    stock_data = fetch_stock_data.read_csv()
    stock_data['year'] = pd.to_datetime(stock_data['date']).dt.year
    stock_data = stock_data.groupby(['symbol', 'year'])['close'].mean().reset_index()
    stock_price_dict = stock_data.pivot(index='year', columns='symbol', values='close').to_dict()
    return stock_price_dict


def calculate_correlation(esg_dict, stock_price_dict):
    correlations = {}
    for symbol in esg_dict:
        if symbol in stock_price_dict:
            esg_scores = []
            stock_changes = []
            for year in esg_dict[symbol]:
                if year in stock_price_dict[symbol]:
                    esg_scores.append(esg_dict[symbol][year])
                    stock_changes.append(stock_price_dict[symbol][year])

            if len(esg_scores) > 1 and len(stock_changes) > 1:
                correlation, _ = pearsonr(esg_scores, stock_changes)
                correlations[symbol] = correlation
            else:
                correlations[symbol] = None
    return correlations


def get_esg_data(request):
    esg_csv_file_path = os.path.join(settings.BASE_DIR, 'data_model', 'ESG_Data.csv')

    try:
        esg_data = load_esg_data(esg_csv_file_path)
        stock_data = load_stock_price_changes()
        correlations = calculate_correlation(esg_data, stock_data)

        return JsonResponse({'status': 'success', 'esg_data': esg_data, 'stock_data': stock_data,
                             'correlations': correlations}, status=200)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
