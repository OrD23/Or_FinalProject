import React, { useState, useEffect } from 'react';
import { useParams }                  from 'react-router-dom';
import axios                          from 'axios';
import jsPDF                          from 'jspdf';
import autoTable                      from 'jspdf-autotable';
import html2canvas                    from 'html2canvas';

import VulnerabilitiesCounter         from './VulnerabilitiesCounter';
import VulnerabilitiesPieChart        from './VulnerabilitiesPieChart';
import OperatingSystemsPieChart       from './OperatingSystemsPieChart';
import AuthenticationPieChart         from './AuthenticationPieChart';
import VulnerabilitiesOverTimeLine    from './VulnerabilitiesOverTimeLine';
import TopVulnerabilitiesList         from './TopVulnerabilitiesList';
import VulnerabilityDropdown          from './VulnerabilityDropdown';
import VulnerabilityModal             from './VulnerabilityModal';

import './Dashboard.css';

const Dashboard = () => {
  const { scanId } = useParams();

  // existing state
  const [apiData, setApiData]       = useState(null);
  const [error, setError]           = useState(null);
  const [chartData, setChartData]   = useState({
    vulnerabilities:        { critical: 0, high: 0, medium: 0, low: 0, info: 0 },
    operatingSystems:       {},
    authentication:         {},
    vulnerabilitiesOverTime:{ dates: [], critical: [], high: [], medium: [], low: [], info: [] },
    topVulnerabilities:     [],
  });

  // ←── ADD THIS: track the selected vulnerability for the modal
  const [selectedVuln, setSelectedVuln] = useState(null);

  useEffect(() => {
    axios.get(`/api/v1/dashboard/${scanId}`)
      .then(res => {
        console.log("dashboard payload:", res.data);
        const data = res.data;

        // ─── Build severity counts ─────────────────────────
        let severityCounts = data.metrics?.vulnerability_counts || {};
        if (!Object.keys(severityCounts).length) {
          severityCounts = { critical:0, high:0, medium:0, low:0, info:0 };
          data.vulnerabilities.forEach(v => {
            const sev = (v.severity || 'info').toLowerCase();
            severityCounts[sev] = (severityCounts[sev] || 0) + 1;
          });
        }

        // ─── Build OS counts ───────────────────────────────
        let osCounts = data.metrics?.operating_system_counts || {};
        if (!Object.keys(osCounts).length) {
          osCounts = {};
          data.vulnerabilities.forEach(v => {
            const os = v.operating_system || 'Other';
            osCounts[os] = (osCounts[os] || 0) + 1;
          });
        }

        // ─── Build auth counts ─────────────────────────────
        let authCounts = data.metrics?.auth_stats || {};
        if (!Object.keys(authCounts).length) {
          authCounts = {};
          data.vulnerabilities.forEach(v => {
            const auth = v.auth || 'without auth';
            authCounts[auth] = (authCounts[auth] || 0) + 1;
          });
        }

        // ─── Build vulnerabilities‐over‐time data ──────────
        const overtime = data.metrics?.vulnerabilities_over_time || {
          dates: [], critical: [], high: [], medium: [], low: [], info: []
        };

        // ─── Top vulnerabilities (critical ones) ──────────
        const topVulns = data.vulnerabilities.filter(
          v => v.severity && v.severity.toLowerCase() === 'critical'
        );

        // ─── Update chartData state ────────────────────────
        setChartData({
          vulnerabilities:        severityCounts,
          operatingSystems:       osCounts,
          authentication:         authCounts,
          vulnerabilitiesOverTime:overtime,
          topVulnerabilities:     topVulns,
        });

        // ─── Finally store raw API data ────────────────────
        setApiData(data);
      })
      .catch(err => {
        console.error('Error fetching dashboard data:', err);
        setError(err);
      });
  }, [scanId]);

  const handleDropdownSelect = vulnId => {
    setSelectedVuln(
      apiData.vulnerabilities.find(v => v.id.toString() === vulnId)
    );
  };
  const closeModal = () => setSelectedVuln(null);

  const downloadPdf = async () => {
    if (!apiData) return;

    // snapshot the dashboard
    const dashboardEl = document.querySelector(".dashboard-container");
    const canvas      = await html2canvas(dashboardEl, { scale: 2 });
    const imgData     = canvas.toDataURL("image/png");

    const pdf = new jsPDF({
      orientation: "landscape",
      unit: "pt",
      format: [dashboardEl.offsetWidth, dashboardEl.offsetHeight]
    });

    // Page 1: dashboard screenshot
    pdf.addImage(imgData, "PNG", 0, 0, dashboardEl.offsetWidth, dashboardEl.offsetHeight);

    // helper to add tables
    const buildTable = (title, rows) => {
      pdf.addPage();
      pdf.setFontSize(16);
      pdf.text(title, 40, 40);
      autoTable(pdf, {
        startY: 60,
        head: [["ID", "CVE Name"]],
        body: rows,
        margin: { left: 40, right: 40 },
        styles: { fontSize: 10 },
        headStyles: { fillColor: [50, 115, 220] }
      });
    };

    // Page 2: all vulns
    const allRows = apiData.vulnerabilities.map(v => [v.id.toString(), v.cve_name]);
    buildTable("All Vulnerabilities", allRows);

    // Page 3: critical only
    const critRows = apiData.vulnerabilities
      .filter(v => v.severity && v.severity.toLowerCase() === "critical")
      .map(v => [v.id.toString(), v.cve_name]);
    buildTable("Critical Vulnerabilities", critRows);

    pdf.save(`scan-${scanId}-report.pdf`);
  };

  if (error)    return <div>Error: {error.message}</div>;
  if (!apiData) return <div>Loading...</div>;

  return (
    <div className="dashboard-container">
      <div className="pdf-button-container">
        <button onClick={downloadPdf} className="pdf-button">
          Download PDF
        </button>
      </div>

        <div className="scan-info">
            <span><strong>Target:</strong> {apiData.scan.target}</span>
        </div>

        <div style={{marginBottom: 20, textAlign: 'center'}}>
            <VulnerabilityDropdown
                vulnerabilities={apiData.vulnerabilities}
          onSelect={handleDropdownSelect}
        />
      </div>

      <div className="dashboard-top">
        <VulnerabilitiesCounter data={chartData.vulnerabilities} />
      </div>

      <div className="dashboard-middle">
        <div className="chart-container">
          <VulnerabilitiesPieChart data={chartData.vulnerabilities} />
        </div>
        <div className="chart-container">
          <OperatingSystemsPieChart data={chartData.operatingSystems} />
        </div>
        <div className="chart-container">
          <AuthenticationPieChart data={chartData.authentication} />
        </div>
      </div>

      <div className="dashboard-bottom">
        <div className="chart-container">
          <VulnerabilitiesOverTimeLine data={chartData.vulnerabilitiesOverTime} />
        </div>
        <div className="list-container">
          <TopVulnerabilitiesList vulnerabilities={chartData.topVulnerabilities} />
        </div>
      </div>

      {selectedVuln && (
        <VulnerabilityModal vulnerability={selectedVuln} onClose={closeModal} />
      )}
    </div>
  );
};

export default Dashboard;
