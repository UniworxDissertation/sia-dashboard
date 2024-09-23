import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const LaggedESGCorrelationChart = () => {
  const [lag, setLag] = useState(1);
  const [correlationData, setCorrelationData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLaggedCorrelationData = async () => {
      try {
        const response = await axios.get(`http://127.0.0.1:8000/api/get-lagged-esg-correlation/?lag=${lag}`);
        const data = response.data.correlations;
        const formattedData = Object.keys(data).map(symbol => ({
          symbol,
          correlation: data[symbol] !== null ? data[symbol].toFixed(2) : 'N/A',
        }));
        setCorrelationData(formattedData);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching lagged correlation data:', error);
        setLoading(false);
      }
    };

    fetchLaggedCorrelationData();
  }, [lag]);

  const handleLagChange = (e) => {
    setLag(Number(e.target.value));
  };

  if (loading) {
    return <div>Loading lagged correlation data...</div>;
  }

  return (
    <div className={"company-select"}>
      <h2>Lagged ESG Correlation Analysis</h2>
      <label htmlFor="lag">Select Lag (years): </label>
      <select className={"lag"} id="company" value={lag} onChange={handleLagChange}>
        {[...Array(5).keys()].map(i => (
          <option key={i + 1} value={i + 1}>
            {i + 1} Year(s)
          </option>
        ))}
      </select>

      <ResponsiveContainer width="100%" height={400}>
        <LineChart
          data={correlationData}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="symbol" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="correlation" stroke="#8884d8" activeDot={{ r: 8 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default LaggedESGCorrelationChart;
