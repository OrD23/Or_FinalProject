// src/components/VulnerabilitiesOverTimeLine.js
import React, { useContext } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from 'chart.js';
import { ThemeContext } from '../ThemeContext';

Chart.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

const VulnerabilitiesOverTimeLine = ({ data }) => {
  const { theme } = useContext(ThemeContext);
  // In dark mode, force pure white ticks; in light mode, force blue (#007bff).
  const tickColor = theme === 'dark' ? '#fff' : '#007bff';
  // Set grid color as desired (here light grid in light mode, slightly visible grid in dark)
  const gridColor = theme === 'dark' ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.1)';
  // Legend text: white in dark, blue in light.
  const legendColor = theme === 'dark' ? '#fff' : '#007bff';

  const { dates, critical, high, medium, low, info } = data;
  const chartData = {
    labels: dates || [],
    datasets: [
      {
        label: 'Critical',
        data: critical || [],
        fill: false,
        backgroundColor: 'rgba(255, 0, 0, 0.6)',
        borderColor: 'rgba(255, 0, 0, 1)',
        tension: 0.4,
      },
      {
        label: 'High',
        data: high || [],
        fill: false,
        backgroundColor: 'rgba(255, 69, 0, 0.6)',
        borderColor: 'rgba(255, 69, 0, 1)',
        tension: 0.4,
      },
      {
        label: 'Medium',
        data: medium || [],
        fill: false,
        backgroundColor: 'rgba(255, 165, 0, 0.6)',
        borderColor: 'rgba(255, 165, 0, 1)',
        tension: 0.4,
      },
      {
        label: 'Low',
        data: low || [],
        fill: false,
        backgroundColor: 'rgba(0, 128, 0, 0.6)',
        borderColor: 'rgba(0, 128, 0, 1)',
        tension: 0.4,
      },
      {
        label: 'Info',
        data: info || [],
        fill: false,
        backgroundColor: 'rgba(0, 0, 255, 0.6)',
        borderColor: 'rgba(0, 0, 255, 1)',
        tension: 0.4,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        ticks: { color: tickColor },
        grid: { color: gridColor },
      },
      y: {
        ticks: { color: tickColor },
        grid: { color: gridColor },
      },
    },
    plugins: {
      legend: {
        labels: { color: legendColor },
      },
    },
  };

  // Using key based on theme forces re-mount when theme changes.
  return (
    <div style={{ height: '100%' }}>
      <Line data={chartData} options={options} key={theme} />
    </div>
  );
};

export default VulnerabilitiesOverTimeLine;
