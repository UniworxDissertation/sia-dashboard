import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import Menu from './Menu';

const Dashboard = () => {
  const [data, setData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [menuOpen, setMenuOpen] = useState(false);
  const [selectedCompany, setSelectedCompany] = useState('');
  const [companies, setCompanies] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:8000/api/stock-data/')
      .then(response => {
        setData(response.data);
        const companyList = [...new Set(response.data.map(item => item.symbol))];
        setCompanies(companyList);
        setSelectedCompany(companyList[0]);
      })
      .catch(error => {
        console.error("There was an error fetching the data!", error);
      });
  }, []);

  useEffect(() => {
    if (selectedCompany) {
      const filtered = data.filter(item => item.symbol === selectedCompany);
      setFilteredData(filtered);
    }
  }, [selectedCompany, data]);

  const handleCompanyChange = (e) => {
    setSelectedCompany(e.target.value);
  };

  return (
    <div className="dashboard">
      <div className="header">
        <button className="menu-button" onClick={() => setMenuOpen(!menuOpen)}>Menu</button>
        {menuOpen && <Menu />}
      </div>
      <div className="company-select">
        <label htmlFor="company">Select Company: </label>
        <select id="company" value={selectedCompany} onChange={handleCompanyChange}>
          {companies.map(company => (
            <option key={company} value={company}>{company}</option>
          ))}
        </select>
      </div>
      <h2>Stock Performance Graph</h2>
      <LineChart width={1000} height={500} data={filteredData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" tickFormatter={(date) => new Date(date).toLocaleDateString()} />
        <YAxis />
        <Tooltip labelFormatter={(date) => new Date(date).toLocaleDateString()}
                 formatter={(value, name, props) => [value, name !== 'symbol' ? name : '']} />
        <Legend />
        <Line type="monotone" dataKey="close" stroke="#82ca9d" name="Close" />
      </LineChart>
    </div>
  );
}

export default Dashboard;
