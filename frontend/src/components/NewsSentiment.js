import React, { useState, useEffect } from 'react';
import axios from 'axios';
import SentimentCard from './SentimentCard';
import Header from './Header';
import PortfolioInsights from "./PortfolioInsights";
import { FaInfoCircle } from 'react-icons/fa';
import { MdClose } from 'react-icons/md';
import Tooltip from 'react-tooltip-lite';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend } from 'recharts';
import SentimentCorrelationChart from "./SentimentCorrelationChart";

const NewsSentiment = () => {
  const [sentiments, setSentiments] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [sentimentData, setSentimentData] = useState([]);
  const [stockData, setStockData] = useState([]);
  const [correlation, setCorrelation] = useState(null);
  const [correlationMeasure, setCorrelationMeasure] = useState('');
  const [volatility, setVolatility] = useState(null);
  const [overallCorrelation, setOverallCorrelation] = useState(null);
  const [showGraphs, setShowGraphs] = useState(false);
  const tickers = ["XOM", "CVX", "NEE", "BP", "SHEL", "JPM", "GS", "BAC", "MS", "WFC"]; // Example tickers

  useEffect(() => {
    const tickersString = tickers.join(', ');
    axios.get('http://localhost:8000/api/process-sentiment/', {
      params: {
        tickers: tickersString
      }
    })
    .then(response => {
      setSentiments(response.data.sentiment_data);
      setOverallCorrelation(response.data.overall_correlation);
    })
    .catch(error => {
      console.error("There was an error fetching the sentiment data!", error);
    });
  }, []);

  const handleCardClick = (company) => {
    setSelectedCompany(company);
    setShowGraphs(true);

    // Fetch sentiment data for the selected company
    axios.get(`http://localhost:8000/api/sentiment-data/`, {
      params: {
        ticker: company
      }
    })
    .then(response => {
      setSentimentData(response.data.sentimentData);
      setStockData(response.data.stockData);
      setCorrelation(response.data.correlation);
      setVolatility(response.data.volatility);
      setCorrelationMeasure(determineCorrelationMeasure(response.data.correlation));
    })
    .catch(error => {
      console.error("There was an error fetching the data!", error);
    });
  };

  const handleCloseClick = () => {
    setShowGraphs(false);
  };

const determineCorrelationMeasure = (correlation) => {
  if (correlation > 0.7) {
    return 'a Strong Positive Correlation, meaning when sentiment is Bullish, stock prices usually rise significantly.';
  } else if (correlation > 0.4) {
    return 'a Moderate Positive Correlation, meaning positive sentiment, such as Somewhat-Bullish, often leads to an increase in stock prices.';
  } else if (correlation > 0.1) {
    return 'a Weak Positive Correlation, meaning there is a slight tendency for stock prices to rise with positive sentiment, even if it is Neutral or Somewhat-Bullish.';
  } else if (correlation > -0.1) {
    return 'No Correlation, meaning sentiment (Neutral or otherwise) and stock prices do not show a consistent pattern.';
  } else if (correlation > -0.4) {
    return 'a Weak Negative Correlation, meaning there is a slight tendency for stock prices to fall with negative sentiment, like Somewhat-Bearish.';
  } else if (correlation > -0.7) {
    return 'a Moderate Negative Correlation, meaning negative sentiment, like Somewhat-Bearish, often leads to a decrease in stock prices.';
  } else {
    return 'a Strong Negative Correlation, meaning when sentiment is Bearish, stock prices usually fall significantly.';
  }
};


  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="label">{`Date: ${label}`}</p>
          <p className="desc">{`Sentiment Label: ${payload[0].payload.Sentiment_Label}`}</p>
        </div>
      );
    }

    return null;
  };

  return (
    <div className="market-sentiments">
      <Header />
      <h2>
        Market Sentiments
        <Tooltip content={
          <div className={"tooltip_content"}>
            <p><strong>Bearish:</strong> Expect a decline in stock price.</p>
            <p><strong>Somewhat-Bearish:</strong> Expect a slight decline in stock price.</p>
            <p><strong>Neutral:</strong> Expect little to no change in stock price.</p>
            <p><strong>Somewhat-Bullish:</strong> Expect a slight increase in stock price.</p>
            <p><strong>Bullish:</strong> Expect a significant increase in stock price.</p>
            <a href="https://www.investopedia.com/terms/b/bullish.asp" target="_blank" rel="noopener noreferrer">Learn more</a>
          </div>
        }>
          <FaInfoCircle style={{ marginLeft: '10px', cursor: 'pointer' }} />
        </Tooltip>
      </h2>
      <div className="sentiment-cards">
        {Object.keys(sentiments).map(ticker => (
          <SentimentCard
            key={ticker}
            company={ticker}
            sentiment={sentiments[ticker].sentiment}
            onClick={handleCardClick}
          />
        ))}
      </div>

      {showGraphs && selectedCompany && (
        <div className="graphs-container">
          <button className="close-button" onClick={handleCloseClick}>
            <MdClose />
          </button>

          <div className="graph">
            <h3>Sentiment Score Variation for {selectedCompany}</h3>
            <LineChart width={500} height={300} data={sentimentData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={['auto', 'auto']} />
              <RechartsTooltip content={<CustomTooltip />} />
              <Legend />
              <Line type="monotone" dataKey="Sentiment_Score" stroke="#8884d8" />
            </LineChart>
          </div>

          <div className="graph">
            <h3>Stock Price Variation for {selectedCompany}</h3>
            <LineChart width={500} height={300} data={stockData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={['auto', 'auto']} /> {/* Adjust this range as needed */}
              <RechartsTooltip formatter={(value, name) => [value, "Close Price"]} />
              <Legend />
              <Line type="monotone" dataKey="close" stroke="#82ca9d" />
            </LineChart>
          </div>

          <div className="graph">
            <h3>Correlation and Volatility Analysis</h3>
            <p><strong>Correlation between Sentiment Score and Stock Price:</strong> {correlation !== null ? correlation.toFixed(2) : 'N/A'}</p>
            <p><strong>Correlation Measure:</strong> {correlationMeasure}</p>
            <p><strong>Stock Price Volatility:</strong> {volatility !== null ? volatility.toFixed(4) : 'N/A'}</p>
          </div>

          <div className="graph">
            <SentimentCorrelationChart selectedTicker={selectedCompany}/>
          </div>
        </div>
  )}

      {overallCorrelation !== null && (
      <div className="overall-correlation">
        <h3>Overall Correlation Analysis</h3>
        <p><strong>Overall Correlation between Market Sentiment and Stock Price across all companies:</strong> {overallCorrelation.toFixed(2)}</p>
        <p>
          Statistically, it is found that market sentiment and stock variations have {determineCorrelationMeasure(overallCorrelation)}.
        </p>
      </div>
      )}
      <PortfolioInsights />
    </div>
  );
}

export default NewsSentiment;
