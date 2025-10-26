// src/components/AuthenticationPieChart.js
import React, { useContext } from 'react';
import { Pie } from 'react-chartjs-2';
import { Chart, ArcElement, Tooltip, Legend } from 'chart.js';
import { ThemeContext } from '../ThemeContext';

Chart.register(ArcElement, Tooltip, Legend);

const AuthenticationPieChart = ({ data }) => {
  const { theme } = useContext(ThemeContext);
  // In light mode, we want blue; in dark mode, white.
  const legendColor = theme === 'dark' ? '#fff' : '#007bff';

  const keys = Object.keys(data);
  const values = Object.values(data);
  const total = values.reduce((a, b) => a + b, 0);
  const percentages =
    total > 0 ? values.map(val => parseFloat(((val / total) * 100).toFixed(1))) : values;

  const chartData = {
    labels: keys,
    datasets: [
      {
        label: 'Authentication Rate (%)',
        data: percentages,
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)',
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: legendColor,
        },
      },
      tooltip: {
        callbacks: {
          label: context => {
            let label = context.label || '';
            if (label) {
              label += ': ';
            }
            label += context.parsed + '%';
            return label;
          },
        },
      },
    },
  };

  // Use key={theme} to force re-render when theme changes.
  return (
    <div style={{ height: '100%' }}>
      <Pie data={chartData} options={options} key={theme} />
    </div>
  );
};

export default AuthenticationPieChart;
