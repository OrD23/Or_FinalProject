// src/components/ThemeToggle.js
import React, { useContext } from 'react';
import { ThemeContext } from '../ThemeContext';

const ThemeToggle = () => {
  const { theme, setTheme } = useContext(ThemeContext);
  return (
    <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>
      {theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
    </button>
  );
};

export default ThemeToggle;
