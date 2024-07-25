import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt.expected_returns import mean_historical_return

# List of tickers
tickers = ['AAPL', 'JNJ', 'JPM', 'PG', 'XOM', 'NEE', 'BA', 'T', 'DOW', 'SPG']

# Fetch historical data
data = yf.download(tickers, start='2018-01-01', end='2023-12-31')['Adj Close']

print(data)

# Calculate expected returns and covariance matrix
mu = mean_historical_return(data)
S = CovarianceShrinkage(data).ledoit_wolf()

# Optimize for maximum Sharpe ratio
ef = EfficientFrontier(mu, S)
weights = ef.max_sharpe()
cleaned_weights = ef.clean_weights()

# Display the portfolio
ef.portfolio_performance(verbose=True)

# Plot the suggested portfolio
labels = cleaned_weights.keys()
sizes = cleaned_weights.values()

fig1, ax1 = plt.subplots()
ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
ax1.axis('equal')  # Equal aspect ratio ensures the pie is drawn as a circle.

plt.title('Suggested Portfolio Allocation')
plt.show()
