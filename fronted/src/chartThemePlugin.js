// src/chartThemePlugin.js
import { Chart } from 'chart.js';

export const themePlugin = {
  id: 'themePlugin',
  beforeDraw: (chart) => {
    // Determine the current theme by checking if the body has the "dark-theme" class.
    const isDarkMode = document.body.classList.contains('dark-theme');

    // Force tick and legend colors.
    const tickColor = isDarkMode ? '#fff' : '#007bff';
    const legendColor = isDarkMode ? '#fff' : '#007bff';
    const gridColor = isDarkMode ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.1)';

    // Update scales (if defined)
    if (chart.options.scales) {
      if (chart.options.scales.x) {
        if (!chart.options.scales.x.ticks) chart.options.scales.x.ticks = {};
        chart.options.scales.x.ticks.color = tickColor;
        if (!chart.options.scales.x.grid) chart.options.scales.x.grid = {};
        chart.options.scales.x.grid.color = gridColor;
      }
      if (chart.options.scales.y) {
        if (!chart.options.scales.y.ticks) chart.options.scales.y.ticks = {};
        chart.options.scales.y.ticks.color = tickColor;
        if (!chart.options.scales.y.grid) chart.options.scales.y.grid = {};
        chart.options.scales.y.grid.color = gridColor;
      }
    }

    // Update legend label color
    if (chart.options.plugins && chart.options.plugins.legend && chart.options.plugins.legend.labels) {
      chart.options.plugins.legend.labels.color = legendColor;
    }
  },
};

// Register the plugin globally.
Chart.register(themePlugin);
