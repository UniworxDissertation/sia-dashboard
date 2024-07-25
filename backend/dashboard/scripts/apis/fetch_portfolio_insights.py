import numpy as np
from django.http import JsonResponse
from scipy.optimize import minimize
from dashboard.scripts.apis import fetch_stock_data

def portfolio_insights(request):
    # Read the CSV data
    data = fetch_stock_data.read_csv()

    # Filter the close prices and pivot for required format
    close_prices = data.pivot(index='date', columns='symbol', values='close')

    # Calculate daily returns
    returns = close_prices.pct_change().dropna()

    # Calculate mean returns and covariance matrix
    mean_returns = returns.mean()
    cov_matrix = returns.cov()

    # Number of assets
    num_assets = len(mean_returns)
    num_portfolios = 10000  # Number of portfolios to simulate

    # Get risk profile from request
    risk_profile = request.GET.get('risk_profile', 'moderate').lower()

    # Set risk-free rate according to risk profile
    risk_free_rate = 0.01  # default to moderate
    if risk_profile == 'low':
        risk_free_rate = 0.02
    elif risk_profile == 'high':
        risk_free_rate = 0.0

    # Initialize arrays to store simulation results
    results = np.zeros((3, num_portfolios))
    weights_record = []

    for i in range(num_portfolios):
        # Generate random weights for the portfolio
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)

        # Store weights
        weights_record.append(weights)

        # Calculate portfolio return and volatility
        portfolio_return = np.sum(weights * mean_returns)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

        # Store results
        results[0, i] = portfolio_return
        results[1, i] = portfolio_volatility
        results[2, i] = (portfolio_return - risk_free_rate) / portfolio_volatility  # Sharpe Ratio

    # Identify the portfolio with the highest Sharpe ratio
    max_sharpe_idx = np.argmax(results[2])
    optimal_weights = weights_record[max_sharpe_idx]

    # Adjust weights according to risk profile
    volatilities = returns.std()
    if risk_profile == 'low':
        optimal_weights = optimal_weights / volatilities
        optimal_weights /= np.sum(optimal_weights)
    elif risk_profile == 'high':
        optimal_weights = optimal_weights * volatilities
        optimal_weights /= np.sum(optimal_weights)

    # Calculate performance of the optimal portfolio
    p_returns, p_volatility = portfolio_performance(optimal_weights, mean_returns, cov_matrix)
    sharpe_ratio = (p_returns - risk_free_rate) / p_volatility

    # Prepare response data
    weights_dict = dict(zip(close_prices.columns, optimal_weights))
    volatility_dict = dict(zip(close_prices.columns, volatilities))
    performance_dict = {
        "expected_annual_return": p_returns,
        "annual_volatility": p_volatility,
        "sharpe_ratio": sharpe_ratio,
    }

    response_data = {
        "weights": weights_dict,
        "volatilities": volatility_dict,
        "performance": performance_dict,
    }

    return JsonResponse(response_data)

def portfolio_performance(weights, mean_returns, cov_matrix):
    returns = np.dot(weights, mean_returns)
    volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    return returns, volatility
