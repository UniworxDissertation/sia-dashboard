from django.http import JsonResponse
from dashboard.scripts.apis import fetch_stock_data
from dashboard.scripts.apis import fetch_user_sentiment
from dashboard.scripts.apis import sentiment_segregation
from dashboard.scripts.apis import fetch_sentiment_and_stock_data
from dashboard.scripts.apis import fetch_user_sentiment_alpha_vantage
from dashboard.scripts.apis import fetch_portfolio_insights
from dashboard.scripts.apis import fetch_alpha_sentiment_and_stock_data
from dashboard.scripts.apis import alpha_sentiment_segregation
from dashboard.scripts.apis import fetch_esg_data

from dashboard.scripts.apis.fetch_sentiment_and_stock_data import fetch_aggregated_correlation

from dashboard.scripts.apis.fetch_sentiment_and_stock_data import fetch_sentiment_and_stock_data_with_lag


def stock_data(request):
    data = fetch_stock_data.read_csv()
    data_list = data.to_dict(orient='records')
    return JsonResponse(data_list, safe=False)


def news_sentiment_view(request):
    tickers = request.GET.get('tickers')
    tickers_list = [ticker.strip() for ticker in tickers.split(',')]
    data = fetch_user_sentiment.fetch_news_sentiment(tickers_list)
    return JsonResponse(data)


def process_sentiment(request):
    tickers = request.GET.get('tickers', '').split(',')
    if not tickers:
        return JsonResponse({'error': 'No tickers provided'}, status=400)

    sentiment_data = sentiment_segregation.process_sentiment_data(request)
    overall_correlation = fetch_aggregated_correlation(tickers)

    response_data = {
        'sentiment_data': {ticker: data for ticker, data in sentiment_data.items()},
        'overall_correlation': overall_correlation
    }

    return JsonResponse(response_data)


def sentiment_and_stock_data_view(request):
    ticker = request.GET.get('ticker')
    if not ticker:
        return JsonResponse({'error': 'Ticker parameter is required'}, status=400)

    try:
        sentiment_data, stock_data, correlation, volatility = (fetch_sentiment_and_stock_data.
                                                               fetch_sentiment_and_stock_data(ticker))
        response_data = {
            'sentimentData': sentiment_data,
            'stockData': stock_data,
            'correlation': correlation,
            'volatility': volatility
        }
        return JsonResponse(response_data)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=500)


def portfolio_insights(request):
    data = fetch_portfolio_insights.portfolio_insights(request)
    return data


def alpha_sentiment_stock_view(request):
    ticker = request.GET.get('ticker', '').upper()
    if not ticker:
        return JsonResponse({'error': 'No ticker provided'}, status=400)

    sentiment_data, stock_data, correlation, volatility = (fetch_alpha_sentiment_and_stock_data.
                                                           fetch_alpha_sentiment_and_stock_data(ticker))

    return JsonResponse({
        'sentimentData': sentiment_data,
        'stockData': stock_data,
        'correlation': correlation,
        'volatility': volatility
    })


def alpha_process_sentiment(request):
    data = alpha_sentiment_segregation.alpha_process_sentiment_data(request)
    return data


def get_alpha_vantage_data(request):
    tickers = request.GET.get('tickers')
    tickers_list = [ticker.strip() for ticker in tickers.split(',')]
    data = fetch_user_sentiment_alpha_vantage.fetch_alpha_news_sentiment(tickers_list)
    return JsonResponse(data)


def get_esg_data(request):
    data = fetch_esg_data.get_esg_data(request)
    return data


def get_sentiment_correlation_with_lag(request, ticker):
    try:
        max_lag = int(request.GET.get('max_lag', 10))  # Default to 10 days
        sentiment_data, stock_data, correlations_by_lag, optimal_lag, optimal_correlation, volatility = fetch_sentiment_and_stock_data_with_lag(
            ticker, max_lag)

        return JsonResponse({
            'status': 'success',
            'sentiment_data': sentiment_data,
            'stock_data': stock_data,
            'correlations_by_lag': correlations_by_lag,
            'optimal_lag': optimal_lag,
            'optimal_correlation': optimal_correlation,
            'volatility': volatility
        }, status=200)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def get_lagged_esg_correlation(request):
    data = fetch_esg_data.get_lagged_esg_correlation(request)
    return data


def sentiment_and_stock_data_with_lag_view(request):
    data = fetch_alpha_sentiment_and_stock_data.sentiment_and_stock_data_with_lag_view(request)
    return data
