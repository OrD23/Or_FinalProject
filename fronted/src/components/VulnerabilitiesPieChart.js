// src/components/VulnerabilitiesPieChart.js
import React, { useContext } from 'react';
import { Pie } from 'react-chartjs-2';
import { Chart, ArcElement, Tooltip, Legend } from 'chart.js';
import { ThemeContext } from '../ThemeContext';

Chart.register(ArcElement, Tooltip, Legend);

const VulnerabilitiesPieChart = ({ data }) => {
  const { theme } = useContext(ThemeContext);
  const legendColor = theme === 'dark' ? '#fff' : '#007bff';

  const { critical = 0, high = 0, medium = 0, low = 0, info = 0 } = data;
  const total = critical + high + medium + low + info;
  const percentages =
    total > 0
      ? [
          ((critical / total) * 100).toFixed(1),
          ((high / total) * 100).toFixed(1),
          ((medium / total) * 100).toFixed(1),
          ((low / total) * 100).toFixed(1),
          ((info / total) * 100).toFixed(1),
        ]
      : [0, 0, 0, 0, 0];
  const percentageData = total > 0 ? percentages.map(val => parseFloat(val)) : [0, 0, 0, 0, 0];

  const chartData = {
    labels: ['Critical', 'High', 'Medium', 'Low', 'Info'],
    datasets: [
      {
        label: 'Vulnerabilities Rate (%)',
        data: percentageData,
        backgroundColor: [
          'rgba(255, 0, 0, 0.6)',
          'rgba(255, 165, 0, 0.6)',
          'rgba(255, 255, 0, 0.6)',
          'rgba(0, 128, 0, 0.6)',
          'rgba(0, 0, 255, 0.6)',
        ],
        borderColor: [
          'rgba(255, 0, 0, 1)',
          'rgba(255, 165, 0, 1)',
          'rgba(255, 255, 0, 1)',
          'rgba(0, 128, 0, 1)',
          'rgba(0, 0, 255, 1)',
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

  return (
    <div style={{ height: '100%' }}>
      <Pie data={chartData} options={options} key={theme} />
    </div>
  );
};

export default VulnerabilitiesPieChart;
