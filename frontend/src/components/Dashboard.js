import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer} from 'recharts';
import Menu from './Menu';
import Header from './Header';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import ESGChart from "./ESGChart";

const Dashboard = () => {
  const [data, setData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [menuOpen, setMenuOpen] = useState(false);
  const [selectedCompany, setSelectedCompany] = useState('');
  const [companies, setCompanies] = useState([]);
  const [startDate, setStartDate] = useState(new Date('2020-01-01'));
  const [endDate, setEndDate] = useState(new Date());

  useEffect(() => {
    axios.get('http://localhost:8000/api/stock-data/')
      .then(response => {
        setData(response.data);
        const companyList = [...new Set(response.data.map(item => item.symbol))];
        setCompanies(companyList);
        setSelectedCompany(companyList[0]);
      })
      .catch(error => {
        console.error('There was an error fetching the data!', error);
      });
  }, []);

  useEffect(() => {
    if (selectedCompany) {
      const filtered = data.filter(item => item.symbol === selectedCompany &&
        new Date(item.date) >= startDate && new Date(item.date) <= endDate);
      setFilteredData(filtered);
    }
  }, [selectedCompany, data, startDate, endDate]);

  const handleCompanyChange = (e) => {
    setSelectedCompany(e.target.value);
  };

  return (
    <div className="dashboard">
      <Header />
      <div className="company-select">
        <label htmlFor="company">Select Company: </label>
        <select id="company" value={selectedCompany} onChange={handleCompanyChange}>
          {companies.map(company => (
            <option key={company} value={company}>{company}</option>
          ))}
        </select>
      </div>
      <div className="custom-date-picker">
        <label>Start Date:</label>
        <DatePicker
          selected={startDate}
          onChange={(date) => setStartDate(date)}
          selectsStart
          startDate={startDate}
          endDate={endDate}
          className="custom-date-input"
          dateFormat="MMM d, yyyy"
        />
        <label>End Date:</label>
        <DatePicker
          selected={endDate}
          onChange={(date) => setEndDate(date)}
          selectsEnd
          startDate={startDate}
          endDate={endDate}
          minDate={startDate}
          className="custom-date-input"
          dateFormat="MMM d, yyyy"
        />
      </div>
      <h2>Stock Performance Graph of {selectedCompany}</h2>
        <ResponsiveContainer width="100%" height={500}>
      <LineChart width={1000} height={500} data={filteredData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" tickFormatter={(date) => new Date(date).toLocaleDateString()} />
        <YAxis />
        <Tooltip labelFormatter={(date) => new Date(date).toLocaleDateString()}
                 formatter={(value, name, props) => [value, name !== 'symbol' ? name : '']} />
        <Legend />
        <Line type="monotone" dataKey="close" stroke="#82ca9d" name="Close" />
      </LineChart>
        </ResponsiveContainer>
      <ESGChart selectedTicker={selectedCompany} />
    </div>
  );
}

export default Dashboard;
