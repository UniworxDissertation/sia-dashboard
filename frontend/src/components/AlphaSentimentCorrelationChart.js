import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import axios from 'axios';

const AlphaSentimentCorrelationChart = ({ correlationsByLag, selectedTicker, optimalLag, optimalCorrelation }) => {


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

export default AlphaSentimentCorrelationChart;
