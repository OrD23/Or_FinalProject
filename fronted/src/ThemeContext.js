import React, { createContext, useState, useEffect } from 'react';
import { Chart } from 'chart.js';

export const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  // Initialize theme from localStorage or default to light.
  const [theme, setTheme] = useState(
    localStorage.getItem('theme') || 'light'
  );

  // Function to update Chart.js defaults based on theme.
  const updateChartDefaults = (currentTheme) => {
    const isDarkMode = currentTheme === 'dark';

    // Legend label colors
    Chart.defaults.plugins.legend = Chart.defaults.plugins.legend || {};
    Chart.defaults.plugins.legend.labels = Chart.defaults.plugins.legend.labels || {};
    Chart.defaults.plugins.legend.labels.color = isDarkMode ? '#fff' : '#007bff';

    // X-axis scaling
    Chart.defaults.scales = Chart.defaults.scales || {};
    Chart.defaults.scales.x = Chart.defaults.scales.x || {};
    Chart.defaults.scales.x.ticks = Chart.defaults.scales.x.ticks || {};
    Chart.defaults.scales.x.ticks.color = isDarkMode ? '#fff' : '#007bff';
    Chart.defaults.scales.x.grid = Chart.defaults.scales.x.grid || {};
    Chart.defaults.scales.x.grid.color = isDarkMode ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.1)';

    // Y-axis scaling
    Chart.defaults.scales.y = Chart.defaults.scales.y || {};
    Chart.defaults.scales.y.ticks = Chart.defaults.scales.y.ticks || {};
    Chart.defaults.scales.y.ticks.color = isDarkMode ? '#fff' : '#007bff';
    Chart.defaults.scales.y.grid = Chart.defaults.scales.y.grid || {};
    Chart.defaults.scales.y.grid.color = isDarkMode ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.1)';
  };

  useEffect(() => {
    const root = document.documentElement;      // <html>
    const body = document.body;                // <body>
    const appRoot = document.getElementById('root'); // React root

    if (theme === 'dark') {
      root.classList.add('dark-theme');
      body.classList.add('dark-theme');
      if (appRoot) appRoot.classList.add('dark-theme');
      // ensure background stays dark
      body.style.backgroundColor = '#1e1e1e';
    } else {
      root.classList.remove('dark-theme');
      body.classList.remove('dark-theme');
      if (appRoot) appRoot.classList.remove('dark-theme');
      body.style.backgroundColor = '';
    }

    localStorage.setItem('theme', theme);
    updateChartDefaults(theme);
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
