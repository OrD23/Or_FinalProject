// frontend/src/components/VulnerabilitiesCounter.js
import React from 'react';

const severityStyles = {
  critical: {
    backgroundColor: '#FF0000', // red
    color: '#fff',
  },
  high: {
    backgroundColor: '#FF4500', // orange-red
    color: '#fff',
  },
  medium: {
    backgroundColor: '#FFA500', // orange
    color: '#fff',
  },
  low: {
    backgroundColor: '#008000', // green
    color: '#fff',
  },
  info: {
    backgroundColor: '#0000FF', // blue
    color: '#fff',
  },
};

const VulnerabilitiesCounter = ({ data }) => {
  // data: { critical, high, medium, low, info }
  return (
    <div style={{ display: 'flex', justifyContent: 'space-around' }}>
      {['critical', 'high', 'medium', 'low', 'info'].map(severity => (
        <div
          key={severity}
          style={{
            ...severityStyles[severity],
            flex: '1',
            margin: '5px',
            padding: '10px',
            textAlign: 'center',
            borderRadius: '5px',
          }}
        >
          <h3 style={{ margin: '0' }}>
            {severity.charAt(0).toUpperCase() + severity.slice(1)}
          </h3>
          <p style={{ fontSize: '2em', margin: '0' }}>{data[severity] || 0}</p>
        </div>
      ))}
    </div>
  );
};

export default VulnerabilitiesCounter;
