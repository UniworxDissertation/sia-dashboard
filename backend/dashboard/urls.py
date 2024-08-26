from django.urls import path
from .views import *

urlpatterns = [
    path('api/stock-data/', stock_data, name='stock_data'),
    path('api/process-sentiment/', process_sentiment, name='process_sentiment'),
    path('api/sentiment-data/', sentiment_and_stock_data_view, name='sentiment_data'),
    path('api/portfolio-insights/', portfolio_insights, name='portfolio-insights'),
    path('api/process-alphasentiment/', alpha_process_sentiment, name='alpha_vantage_sentiments'),
    path('api/alphasentiment-data/', alpha_sentiment_stock_view, name='alpha_sentiment_stock_view'),
    path('api/refresh-sentiment-data/', get_alpha_vantage_data, name='get_alpha_vantage_data'),
    path('api/get-esg-data/', get_esg_data, name='get_esg_data'),
    path('api/get-sentiment-correlation-with-lag/<str:ticker>/', get_sentiment_correlation_with_lag,
         name='get_sentiment_correlation_with_lag'),
    path('api/get-lagged-esg-correlation/', get_lagged_esg_correlation, name='get_lagged_esg_correlation'),
    path('api/alphasentiment-data-with-lag/', sentiment_and_stock_data_with_lag_view, name='sentiment_and_stock_data_with_lag_view')
]
