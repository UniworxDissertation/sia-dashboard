import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from django.http import JsonResponse
import os

from dashboard.scripts.apis import fetch_stock_data


def load_financial_indicators(file_path):
    indicators = pd.read_csv(file_path)
    indicators['date'] = pd.to_datetime(indicators['date'])
    indicators.set_index(['date', 'symbol'], inplace=True)
    return indicators


csv_path = (os.path.dirname(os.path.abspath(__file__)).replace('scripts\\apis',
                                                               'data_model/Historical_Financial_Indicators.csv')
            .replace('\\dashboard', ''))

financial_indicators = load_financial_indicators(csv_path)


def merge_stock_and_indicators(stock_data, indicators):
    stock_data['date'] = pd.to_datetime(stock_data['date'])
    merged_data = stock_data.merge(indicators, on=['date', 'symbol'], how='left')
    merged_data.fillna(merged_data.mean(), inplace=True)
    return merged_data


def train_model(merged_data):
    features = ['close', 'volume', 'EPS', 'PE', 'ROE', 'ROA', 'ROI']
    X = merged_data[features]
    y = merged_data['close'].shift(-1).fillna(method='ffill')

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    merged_data['predicted_close'] = model.predict(X)
    return model


def calculate_investment_growth(start_date, end_date, weights, stock_data, initial_investment=100):
    start_prices = stock_data[stock_data['date'] == start_date].set_index('symbol')['predicted_close']
    end_prices = stock_data[stock_data['date'] == end_date].set_index('symbol')['predicted_close']

    if start_prices.empty or end_prices.empty:
        return estimate_portfolio_value(weights, stock_data, initial_investment, end_date)

    growth = (end_prices / start_prices) * weights
    total_growth = (growth.sum() - 1)

    portfolio_value = initial_investment * (1 + total_growth)
    return portfolio_value


def estimate_portfolio_value(weights, stock_data, initial_investment=100, target_date=None):
    close_prices = stock_data.pivot(index='date', columns='symbol', values='close')
    returns = close_prices.pct_change().dropna()
    mean_returns = returns.mean()
    cov_matrix = returns.cov()

    num_simulations = 10000

    if target_date:
        current_date = datetime.now().date()
        target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        num_days = np.busday_count(current_date, target_date)
    else:
        num_days = 252

    simulated_portfolio_values = []

    for _ in range(num_simulations):
        daily_returns = np.random.multivariate_normal(mean_returns, cov_matrix, num_days)
        price_paths = np.exp(np.cumsum(daily_returns, axis=0))
        if len(price_paths) > 0:
            final_prices = price_paths[-1, :]
            portfolio_growth = np.dot(final_prices, weights)
            simulated_portfolio_values.append(portfolio_growth)
        else:
            return None

    estimated_value = initial_investment * np.mean(simulated_portfolio_values)
    return estimated_value


def portfolio_insights(request):
    data = fetch_stock_data.read_csv()
    merged_data = merge_stock_and_indicators(data, financial_indicators)
    model = train_model(merged_data)

    close_prices = merged_data.pivot(index='date', columns='symbol', values='close')
    returns = close_prices.pct_change().dropna()

    mean_returns = returns.mean()
    cov_matrix = returns.cov()

    num_assets = len(mean_returns)
    num_portfolios = 10000

    risk_profile = request.GET.get('risk_profile', 'moderate').lower()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    risk_free_rate = 0.01
    if risk_profile == 'low':
        risk_free_rate = 0.0
    elif risk_profile == 'high':
        risk_free_rate = 0.02

    np.random.seed(42)

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

    p_returns, p_volatility = results[0, max_sharpe_idx], results[1, max_sharpe_idx]
    sharpe_ratio = results[2, max_sharpe_idx]

    investment_growth = None
    if start_date and end_date:
        investment_growth = calculate_investment_growth(start_date, end_date, optimal_weights, merged_data)

    weights_dict = dict(zip(close_prices.columns, optimal_weights))
    volatility_dict = dict(zip(close_prices.columns, returns.std()))
    performance_dict = {
        "expected_annual_return": p_returns,
        "annual_volatility": p_volatility,
        "sharpe_ratio": sharpe_ratio,
    }

    response_data = {
        "weights": weights_dict,
        "volatilities": volatility_dict,
        "performance": performance_dict,
        "investment_growth": investment_growth,
    }

    return JsonResponse(response_data)
