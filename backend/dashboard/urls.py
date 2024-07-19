from django.urls import path
from .views import stock_data, news_sentiment_view, process_sentiment

urlpatterns = [
    path('api/stock-data/', stock_data, name='stock_data'),
    path('api/sentiment-data', news_sentiment_view, name='news_sentiment_view'),
    path('api/process-sentiment/', process_sentiment, name='process_sentiment')
]