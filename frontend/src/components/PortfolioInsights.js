import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';

const PortfolioInsights = () => {
  const [data, setData] = useState([]);
  const [zeroAllocation, setZeroAllocation] = useState([]);
  const [riskProfile, setRiskProfile] = useState('moderate');

  const fetchPortfolioData = (profile) => {
    axios.get('http://localhost:8000/api/portfolio-insights/', {
      params: { risk_profile: profile }
    })
    .then(response => {
      const weights = response.data.weights;
      const volatilities = response.data.volatilities;
      const formattedData = [];
      const zeroAllocationData = [];

      Object.keys(weights).forEach(key => {
        const value = weights[key] * 100;  // Convert to percentage
        const volatility = volatilities[key] * 100;  // Convert to percentage
        if (value.toFixed(0) > 0) {
          formattedData.push({ name: key, value, volatility });
        } else {
          zeroAllocationData.push(key);
        }
      });

      setData(formattedData);
      setZeroAllocation(zeroAllocationData);
    })
    .catch(error => {
      console.error('Error fetching portfolio insights:', error);
    });
  };

  useEffect(() => {
    fetchPortfolioData(riskProfile);
  }, [riskProfile]);

  const handleRiskProfileChange = (event) => {
    setRiskProfile(event.target.value);
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#FFBB99', '#99CCFF', '#FF6666', '#FFCC00', '#66CC99', '#3399FF'];

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const { name, value, volatility } = payload[0].payload;
      return (
        <div className="custom-tooltip">
          <p>{`${name}: ${value.toFixed(2)}%`}</p>
          <p>{`Volatility: ${volatility.toFixed(2)}%`}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="portfolio-insights">
      <h2>Portfolio Diversification Insights</h2>
      <div className="risk-profile-select">
        <label htmlFor="risk-profile">Select Risk Profile: </label>
        <select id="risk-profile" value={riskProfile} onChange={handleRiskProfileChange}>
          <option value="low">Low Risk</option>
          <option value="moderate">Moderate Risk</option>
          <option value="high">High Risk</option>
        </select>
      </div>
      <PieChart width={600} height={350}>
        <Pie
          data={data}
          cx={300}
          cy={150}
          labelLine={false}
          label={({ name, percent }) => (percent * 100).toFixed(0) > 0 ? `${name}: ${(percent * 100).toFixed(0)}%` : ''}  // Updated line
          outerRadius={120}
          fill="#8884d8"
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        <Legend layout="horizontal" verticalAlign="bottom" align="center" />
      </PieChart>

      {zeroAllocation.length > 0 && (
        <div className="zero-allocation">
          <h3>Companies with 0% Allocation</h3>
          <ul>
            {zeroAllocation.map(company => (
              <li key={company}>{company}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default PortfolioInsights;
