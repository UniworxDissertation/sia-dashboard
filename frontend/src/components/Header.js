import React, { useState } from 'react';
import Menu from './Menu';  // Adjust the import path according to your project structure

const Header = () => {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="header">
      <a className="sia-logo" href="/">SIA - Dashboard</a>
      <div
        className="menu-container"
        onMouseEnter={() => setMenuOpen(true)}
        onMouseLeave={() => setMenuOpen(false)}
      >
        <button
          className="menu-button"
          onClick={() => setMenuOpen(!menuOpen)}
        >
          Menu
        </button>
        <Menu
          menuOpen={menuOpen}
          onMouseEnter={() => setMenuOpen(true)}
          onMouseLeave={() => setMenuOpen(false)}
        />
      </div>
    </div>
  );
};

export default Header;
