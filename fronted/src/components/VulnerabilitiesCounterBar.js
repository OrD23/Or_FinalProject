// frontend/src/components/VulnerabilitiesCounterBar.js
import React from 'react';
import { Bar } from 'react-chartjs-2';
import { Chart, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js';

Chart.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

const VulnerabilitiesCounterBar = ({ data }) => {
  // data expected: { critical, high, medium, low, info }
  const chartData = {
    labels: ['Critical', 'High', 'Medium', 'Low', 'Info'],
    datasets: [{
      label: 'Vulnerabilities Count',
      data: [
        data.critical || 0,
        data.high || 0,
        data.medium || 0,
        data.low || 0,
        data.info || 0,
      ],
      backgroundColor: [
        'rgba(255, 0, 0, 0.6)',       // Critical – red
        'rgba(255, 165, 0, 0.6)',     // High – orange
        'rgba(255, 255, 0, 0.6)',     // Medium – yellow
        'rgba(0, 128, 0, 0.6)',       // Low – green
        'rgba(0, 0, 255, 0.6)',       // Info – blue
      ],
      borderColor: [
        'rgba(255, 0, 0, 1)',
        'rgba(255, 165, 0, 1)',
        'rgba(255, 255, 0, 1)',
        'rgba(0, 128, 0, 1)',
        'rgba(0, 0, 255, 1)',
      ],
      borderWidth: 1,
    }],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
  };

  return (
    <div style={{ height: '100%' }}>
      <Bar data={chartData} options={options} />
    </div>
  );
};

export default VulnerabilitiesCounterBar;
