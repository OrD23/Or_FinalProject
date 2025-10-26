// frontend/src/components/TopVulnerabilitiesList.js
import React from 'react';

const TopVulnerabilitiesList = ({ vulnerabilities }) => {
  return (
    <div style={{ overflowY: 'auto', maxHeight: '100%' }}>
      <h3>Top Critical Vulnerabilities</h3>
      <ul>
        {vulnerabilities.map(vuln => (
          <li key={vuln.id}>
            <strong>{vuln.cve_id}</strong>: {vuln.description} (Severity: {vuln.severity_score})
          </li>
        ))}
      </ul>
    </div>
  );
};

export default TopVulnerabilitiesList;
