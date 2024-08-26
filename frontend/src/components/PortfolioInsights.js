import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

const PortfolioInsights = () => {
  const [data, setData] = useState([]);
  const [zeroAllocation, setZeroAllocation] = useState([]);
  const [riskProfile, setRiskProfile] = useState('moderate');
  const [startDate, setStartDate] = useState(new Date());
  const [endDate, setEndDate] = useState(new Date());
  const [investmentGrowth, setInvestmentGrowth] = useState(null);
  const [loading, setLoading] = useState(false);  // Add loading state

  const fetchPortfolioData = (profile, start, end) => {
    setLoading(true);  // Set loading to true when starting the API call
    axios.get('http://localhost:8000/api/portfolio-insights/', {
      params: { risk_profile: profile, start_date: start, end_date: end }
    })
    .then(response => {
      const weights = response.data.weights;
      const volatilities = response.data.volatilities;
      const formattedData = [];
      const zeroAllocationData = [];

      Object.keys(weights).forEach(key => {
        const value = weights[key] * 100;
        const volatility = volatilities[key] * 100;
        if (value.toFixed(0) > 0) {
          formattedData.push({ name: key, value, volatility });
        } else {
          zeroAllocationData.push(key);
        }
      });

      setData(formattedData);
      setZeroAllocation(zeroAllocationData);
      setInvestmentGrowth(response.data.investment_growth);
      setLoading(false);  // Set loading to false when data is loaded
    })
    .catch(error => {
      console.error('Error fetching portfolio insights:', error);
      setLoading(false);  // Set loading to false even if there's an error
    });
  };

  useEffect(() => {
    fetchPortfolioData(riskProfile, startDate.toISOString().split('T')[0], endDate.toISOString().split('T')[0]);
  }, [riskProfile, startDate, endDate]);

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

  const isWeekday = date => {
    const day = date.getDay();
    return day !== 0 && day !== 6;
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
      <div className="date-picker-container">
        <label htmlFor="start-date">Start Date: </label>
        <DatePicker
          selected={startDate}
          onChange={(date) => setStartDate(date)}
          selectsStart
          startDate={startDate}
          endDate={endDate}
          filterDate={isWeekday}
          dateFormat="yyyy-MM-dd"
        />
        <label htmlFor="end-date">End Date: </label>
        <DatePicker
          selected={endDate}
          onChange={(date) => setEndDate(date)}
          selectsEnd
          startDate={startDate}
          endDate={endDate}
          minDate={startDate}
          filterDate={isWeekday}
          dateFormat="yyyy-MM-dd"
        />
      </div>
      <div className="insights-container">
        <div className="chart-container">
          {loading ? (  // Show loading indicator while data is being fetched
            <div>Loading chart...</div>
          ) : (
            <PieChart width={600} height={350}>
              <Pie
                data={data}
                cx={300}
                cy={150}
                labelLine={false}
                label={({ name, percent }) => (percent * 100).toFixed(0) > 0 ? `${name}: ${(percent * 100).toFixed(0)}%` : ''}
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
          )}

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

        {loading ? (  // Show loading indicator for investment growth while data is being fetched
          <div>Loading investment growth...</div>
        ) : (
          investmentGrowth !== null && (
            <div className="investment-growth">
              <h3>Investment Growth</h3>
              <p>If you had invested $100 on {startDate.toISOString().split('T')[0]},
                it would be worth ${investmentGrowth.toFixed(2)} on {endDate.toISOString().split('T')[0]}.</p>
            </div>
          )
        )}
      </div>
    </div>
  );
}

export default PortfolioInsights;
