import os

from django.http import JsonResponse
import numpy as np
import pandas as pd
from datetime import timedelta
from sklearn.ensemble import RandomForestRegressor
from dashboard.scripts.apis import fetch_stock_data
from sklearn.model_selection import train_test_split

from dashboard.scripts.apis.fetch_portfolio_insights import estimate_portfolio_value


def load_financial_indicators(file_path):
    indicators = pd.read_csv(file_path)
    indicators['date'] = pd.to_datetime(indicators['date'])
    indicators.set_index(['date', 'symbol'], inplace=True)
    return indicators


# Path to financial indicators CSV file
csv_path = (os.path.dirname(os.path.abspath(__file__)).replace('scripts\\apis', 'data_model/Historical_Financial_Indicators.csv').replace('\\dashboard', ''))
financial_indicators = load_financial_indicators(csv_path)


def merge_stock_and_indicators(stock_data, indicators):
    stock_data['date'] = pd.to_datetime(stock_data['date'])
    merged_data = stock_data.merge(indicators, on=['date', 'symbol'], how='left')
    merged_data.fillna(merged_data.mean(), inplace=True)
    return merged_data


def train_model(merged_data):
    features = ['volume', 'EPS', 'PE', 'ROE', 'ROA', 'ROI']
    X = merged_data[features]
    y = merged_data['close'].shift(-1).fillna(method='ffill')

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, min_samples_split=2, max_depth=10, random_state=42)
    model.fit(X_train, y_train)

    merged_data['predicted_close'] = model.predict(X)
    return model


def backtest_portfolio_insights(merged_data, num_portfolios, risk_free_rate, start_date, end_date):
    close_prices = merged_data.pivot(index='date', columns='symbol', values='close')
    returns = close_prices.pct_change().dropna()

    mean_returns = returns.mean()
    cov_matrix = returns.cov()

    num_assets = len(mean_returns)

    results = np.zeros((3, num_portfolios))
    weights_record = []

    for i in range(num_portfolios):
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)

        weights_record.append(weights)

        portfolio_return = np.sum(weights * mean_returns)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

        results[0, i] = portfolio_return
        results[1, i] = portfolio_volatility
        results[2, i] = (portfolio_return - risk_free_rate) / portfolio_volatility

    max_sharpe_idx = np.argmax(results[2])
    optimal_weights = weights_record[max_sharpe_idx]

    # Calculating portfolio growth
    actual_growth = (merged_data[merged_data['date'] == end_date]['close'].mean() /
                     merged_data[merged_data['date'] == start_date]['close'].mean()) - 1

    return optimal_weights, actual_growth


def calculate_growth_difference(merged_data, optimal_weights, actual_growth, backtest_start_date, initial_investment=100):
    predicted_portfolio_value = estimate_portfolio_value(optimal_weights, merged_data, backtest_start_date)
    predicted_growth = predicted_portfolio_value / initial_investment - 1

    # Calculate growth difference percentage
    growth_difference_percentage = ((predicted_growth - actual_growth) / actual_growth) * 100 if actual_growth != 0 else None
    return predicted_growth, growth_difference_percentage


def backtest_only_endpoint(request):
    data = fetch_stock_data.read_csv()
    merged_data = merge_stock_and_indicators(data, financial_indicators)

    last_date = merged_data['date'].max()
    backtest_end_date = last_date
    backtest_start_date = backtest_end_date - timedelta(days=365 * 2)

    risk_free_rates = [0.0, 0.01, 0.02]
    num_portfolios = 5000

    results_by_risk_rate = {}

    for risk_free_rate in risk_free_rates:
        optimal_weights, actual_growth = backtest_portfolio_insights(merged_data, num_portfolios, risk_free_rate,
                                                                     backtest_start_date, backtest_end_date)
        predicted_growth, growth_difference_percentage = calculate_growth_difference(merged_data, optimal_weights, actual_growth,
                                                                   backtest_start_date)

        if growth_difference_percentage is not None:
            results_by_risk_rate[risk_free_rate] = {
                "growth_difference_percentage": growth_difference_percentage,
                "actual_growth": actual_growth,
                "predicted_growth": predicted_growth
            }

    return JsonResponse(results_by_risk_rate)
