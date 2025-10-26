// src/chartDefaults.js
import { Chart } from 'chart.js';

export const setGlobalChartDefaults = () => {
  const rootStyles = getComputedStyle(document.documentElement);
  const textColor = rootStyles.getPropertyValue('--text-color').trim();
  const bgColor = rootStyles.getPropertyValue('--bg-color').trim();
  const isDarkMode = bgColor === '#000'; // assuming dark mode uses pure black

  // Update legend labels globally:
  Chart.defaults.plugins.legend.labels.color = isDarkMode ? '#fff' : textColor;

  // Optionally, update tick defaults:
  Chart.defaults.scales.x.ticks.color = isDarkMode ? '#fff' : textColor;
  Chart.defaults.scales.y.ticks.color = isDarkMode ? '#fff' : textColor;

  // And grid line defaults:
  Chart.defaults.scales.x.grid.color = isDarkMode ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.1)';
  Chart.defaults.scales.y.grid.color = isDarkMode ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.1)';
};
