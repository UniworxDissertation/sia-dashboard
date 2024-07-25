from django.urls import path
from .views import *

urlpatterns = [
    path('api/stock-data/', stock_data, name='stock_data'),
    path('api/sentiment-data', news_sentiment_view, name='news_sentiment_view'),
    path('api/process-sentiment/', process_sentiment, name='process_sentiment'),
    path('api/sentiment-data/', sentiment_and_stock_data_view, name='sentiment_data'),
    path('api/portfolio-insights/', portfolio_insights, name='portfolio-insights')
]