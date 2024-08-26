import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import axios from 'axios';

const SentimentCorrelationChart = ({ selectedTicker }) => {
  const [correlationsByLag, setCorrelationsByLag] = useState([]);
  const [optimalLag, setOptimalLag] = useState(null);
  const [optimalCorrelation, setOptimalCorrelation] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCorrelationData = async () => {
      try {
        const response = await axios.get(`http://127.0.0.1:8000/api/get-sentiment-correlation-with-lag/${selectedTicker}`);
        const { correlations_by_lag, optimal_lag, optimal_correlation } = response.data;

        // Convert the correlations_by_lag object to a format suitable for charting
        const chartData = Object.keys(correlations_by_lag).map(lag => ({
          lag: parseInt(lag),
          correlation: correlations_by_lag[lag]
        }));

        setCorrelationsByLag(chartData);
        setOptimalLag(optimal_lag);
        setOptimalCorrelation(optimal_correlation);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching correlation data:', error);
        setLoading(false);
      }
    };

    fetchCorrelationData();
  }, [selectedTicker]);

  if (loading) {
    return <div>Loading correlation data...</div>;
  }

  return (
    <div>
      <h2>Correlation by Lag for {selectedTicker}</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={correlationsByLag} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="lag" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="correlation" fill="#8884d8" />
        </BarChart>
      </ResponsiveContainer>

      <h3>Optimal Lag: {optimalLag} days</h3>
      <h3>Optimal Correlation: {optimalCorrelation ? optimalCorrelation.toFixed(2) : 'N/A'}</h3>
    </div>
  );
};

export default SentimentCorrelationChart;
