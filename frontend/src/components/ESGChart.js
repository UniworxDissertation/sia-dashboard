import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';
import LaggedESGCorrelationChart from "./LaggedESGCorrelationChart";

const ESGChart = ({ selectedTicker }) => {
  const [data, setData] = useState({ esg_data: {}, stock_data: {}, correlations: {} });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/get-esg-data/');
        setData(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching ESG and stock data:', error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const esgChartData = Object.keys(data.esg_data[selectedTicker] || {}).map(year => ({
    year,
    esgScore: data.esg_data[selectedTicker][year],
  }));

  const stockChartData = Object.keys(data.stock_data[selectedTicker] || {}).map(year => ({
    year,
    stockPrice: data.stock_data[selectedTicker][year],
  }));

  if (loading) {
    return <div>Loading ESG and stock data...</div>;
  }

  return (
    <div>
      <h2>ESG and Stock Performance Charts for {selectedTicker}</h2>
      <div style={{ display: 'flex', justifyContent: 'space-around' }}>
        <ResponsiveContainer width="45%" height={300}>
          <LineChart data={esgChartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="year" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="esgScore" stroke="#8884d8" strokeWidth={3} activeDot={{ r: 8 }} />
          </LineChart>
        </ResponsiveContainer>

        <ResponsiveContainer width="45%" height={300}>
          <LineChart data={stockChartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="year" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="stockPrice" stroke="#82ca9d" strokeWidth={3} activeDot={{ r: 8 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <h3>Correlation between ESG Score and Stock Price: {data.correlations[selectedTicker]?.toFixed(2)}</h3>
    <LaggedESGCorrelationChart />
    </div>
  );
};

export default ESGChart;
