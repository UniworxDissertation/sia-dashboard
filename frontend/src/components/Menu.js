import React from 'react';

const Menu = ({ menuOpen, onMouseEnter, onMouseLeave }) => {
  return (
    <div
      className="menu-list"
      style={{ display: menuOpen ? 'block' : 'none' }}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      <a href="/">Dashboard</a>
      <a href="/news-sentiment">News Sentiment</a>
    </div>
  );
};

export default Menu;
