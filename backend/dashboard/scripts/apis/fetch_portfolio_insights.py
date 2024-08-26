import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split, ParameterGrid
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
    model = RandomForestRegressor(n_estimators=50, min_samples_split=10, random_state=42)
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


def backtest_estimate_portfolio_value(weights, stock_data, initial_investment=100,
                                      num_simulations=10000, num_days=252,
                                      custom_returns=None):
    """
    This function mirrors the original `estimate_portfolio_value` but accepts
    additional parameters for backtesting, such as custom returns, and allows
    tuning of Monte Carlo simulation parameters without affecting the main function.

    :param weights: Array of weights for different stocks in the portfolio.
    :param stock_data: The stock data used for simulation.
    :param initial_investment: Initial investment amount.
    :param num_simulations: Number of Monte Carlo simulations to run.
    :param num_days: Number of days for the simulation (e.g., 252 for a year).
    :param custom_returns: Custom returns to use instead of calculating from stock data (useful for testing).
    :return: Estimated portfolio value after simulation.
    """
    close_prices = stock_data.pivot(index='date', columns='symbol', values='close')

    if custom_returns is None:
        returns = close_prices.pct_change().dropna()
    else:
        returns = custom_returns

    mean_returns = returns.mean()
    cov_matrix = returns.cov()

    simulated_portfolio_values = []

    for _ in range(num_simulations):
        # Generate random daily returns using multivariate normal distribution
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


# Define the parameter grid for RandomForest and Monte Carlo simulation
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5, 10],
    'num_simulations': [1000, 5000, 10000],
    'num_days': [252, 500],
    'risk_free_rate': [0.0, 0.01, 0.02],
}


def backtest_portfolio(start_date, end_date, weights, stock_data):
    start_prices = stock_data[stock_data['date'] == start_date].set_index('symbol')['predicted_close']
    end_prices = stock_data[stock_data['date'] == end_date].set_index('symbol')['predicted_close']

    if start_prices.empty or end_prices.empty:
        return None, None

    growth = (end_prices / start_prices) * weights
    total_growth = (growth.sum() - 1)

    portfolio_value = 100 * (1 + total_growth)  # Assuming initial investment of 100
    return portfolio_value, total_growth


def backtest_and_tune_monte_carlo_insights(request):
    data = fetch_stock_data.read_csv()
    merged_data = merge_stock_and_indicators(data, financial_indicators)

    # Determine the last date in the dataset
    last_date = merged_data['date'].max()

    # Set the start and end dates for the testing period (last 2 years)
    backtest_end_date = last_date
    backtest_start_date = backtest_end_date - timedelta(days=2 * 365)

    np.random.seed(42)

    # Set the training period (everything before the last 2 years)
    train_data = merged_data[merged_data['date'] < backtest_start_date]
    test_data = merged_data[(merged_data['date'] >= backtest_start_date) & (merged_data['date'] <= backtest_end_date)]

    best_error = np.inf
    best_params = None
    best_portfolio_value = None
    best_actual_value = None
    best_growth_difference_percentage = None
    best_actual_growth = None
    best_predicted_growth = None

    # Iterate through all combinations of hyperparameters
    for params in ParameterGrid(param_grid):
        # Train the RandomForestRegressor model with current parameters
        model = RandomForestRegressor(n_estimators=params['n_estimators'],
                                      max_depth=params['max_depth'],
                                      min_samples_split=params['min_samples_split'],
                                      random_state=42)
        model.fit(train_data[['close', 'volume', 'EPS', 'PE', 'ROE', 'ROA', 'ROI']],
                  train_data['close'].shift(-1).fillna(method='ffill'))

        # Generate predictions on the test data
        test_data['predicted_close'] = model.predict(
            test_data[['close', 'volume', 'EPS', 'PE', 'ROE', 'ROA', 'ROI']])

        # Simulate portfolio performance on the test data using Monte Carlo simulation
        optimal_weights = np.random.random(len(test_data['symbol'].unique()))  # Using random weights for example
        optimal_weights /= np.sum(optimal_weights)  # Normalize weights

        portfolio_value = backtest_estimate_portfolio_value(optimal_weights, test_data,
                                                            num_simulations=params['num_simulations'],
                                                            num_days=params['num_days'])

        # Calculate actual performance
        actual_growth = (test_data[test_data['date'] == backtest_end_date]['close'].mean() /
                         test_data[test_data['date'] == backtest_start_date]['close'].mean()) - 1
        actual_portfolio_value = 100 * (1 + actual_growth)

        # Calculate the difference between predicted and actual growth in percentage
        predicted_growth = portfolio_value / 100 - 1  # Calculate predicted growth from portfolio value
        growth_difference_percentage = ((
                                                predicted_growth - actual_growth) / actual_growth) * 100 \
            if actual_growth != 0 else None

        # Track the best parameters based on the lowest error
        if growth_difference_percentage is not None and abs(growth_difference_percentage) < best_error:
            best_error = abs(growth_difference_percentage)
            best_params = params
            best_portfolio_value = portfolio_value
            best_actual_value = actual_portfolio_value
            best_growth_difference_percentage = growth_difference_percentage
            best_actual_growth = actual_growth
            best_predicted_growth = predicted_growth

    response_data = {
        "predicted_portfolio_value": best_portfolio_value,
        "predicted_growth": best_predicted_growth,
        "actual_growth": best_actual_growth,
        "growth_difference_percentage": best_growth_difference_percentage,
        "actual_portfolio_value": best_actual_value,
        "best_parameters": best_params
    }

    return JsonResponse(response_data)
