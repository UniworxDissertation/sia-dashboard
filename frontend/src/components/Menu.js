import React from 'react';
import { Link } from 'react-router-dom';

const Menu = () => {
  return (
    <div className="menu">
      <Link to="/">Dashboard</Link>
      <Link to="/news-sentiment">News Sentiment</Link>
    </div>
  );
}

export default Menu;
