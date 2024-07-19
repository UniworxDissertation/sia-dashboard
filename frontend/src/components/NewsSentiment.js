import React, { useState, useEffect } from 'react';
import axios from 'axios';
import SentimentCard from './SentimentCard';

const NewsSentiment = () => {
  const [sentiments, setSentiments] = useState([]);
  const tickers = ["XOM","CVX","NEE","BP","SHEL","JPM","GS","BAC","MS","WFC"]; // Example tickers

  useEffect(() => {
    const tickersString = tickers.join(', ').replaceAll(" ", "");
    console.log(tickersString)
    axios.get('http://localhost:8000/api/process-sentiment', {
      params: {
        tickers: tickersString
      }
    })
    .then(response => {
      setSentiments(response.data);
    })
    .catch(error => {
      console.error("There was an error fetching the sentiment data!", error);
    });
  }, []);

  return (
    <div className="market-sentiments">
      <h2>Market Sentiments</h2>
      <div className="sentiment-cards">
        {Object.keys(sentiments).map(ticker => (
          <SentimentCard
            key={ticker}
            company={ticker}
            sentiment={sentiments[ticker].sentiment} // Adjust this based on actual data structure
          />
        ))}
      </div>
    </div>
  );
}

export default NewsSentiment;