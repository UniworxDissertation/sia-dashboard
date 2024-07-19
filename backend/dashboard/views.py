from django.http import JsonResponse
from dashboard.scripts.apis import fetch_stock_data
from dashboard.scripts.apis import fetch_user_sentiment
from dashboard.scripts.apis import sentiment_segregation


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
    data = sentiment_segregation.process_sentiment_data(request)
    return data
