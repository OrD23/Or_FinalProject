import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './OrganizationDashboard.css';

const OrganizationDashboard = () => {
  // Hide global footer while mounted
  useEffect(() => {
    document.body.classList.add('hide-footer');
    return () => document.body.classList.remove('hide-footer');
  }, []);

  const navigate = useNavigate();
  const [orgs, setOrgs] = useState([]);
  const [selectedOrgId, setSelectedOrgId] = useState('');
  const [assets, setAssets] = useState([]);
  const [newAsset, setNewAsset] = useState({ value: '', asset_type: 'ip', is_internal: false });
  const [selectedAssetId, setSelectedAssetId] = useState('');
  const [scans, setScans] = useState([]);
  const [needsManualIp, setNeedsManualIp] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [manualIp, setManualIp] = useState('');

  // load organizations
  useEffect(() => {
    axios.get('/api/v1/organizations/')
      .then(res => setOrgs(res.data))
      .catch(console.error);
  }, []);

  // load assets & scans when org selected
  useEffect(() => {
    if (!selectedOrgId) {
      setAssets([]);
      setScans([]);
      setSelectedAssetId('');
      return;
    }
    axios.get(`/api/v1/organizations/${selectedOrgId}/assets`)
      .then(res => {
        setAssets(res.data);
        if (res.data.length) setSelectedAssetId(res.data[0].id.toString());
      })
      .catch(console.error);
    axios.get(`/api/v1/organizations/${selectedOrgId}/scans`)
      .then(res => setScans(res.data))
      .catch(console.error);
    setNeedsManualIp(false);
  }, [selectedOrgId]);

  const handleAddAsset = async () => {
    if (!newAsset.value.trim()) return;
    try {
      await axios.post(
        `/api/v1/organizations/${selectedOrgId}/assets`, newAsset
      );
      const { data } = await axios.get(`/api/v1/organizations/${selectedOrgId}/assets`);
      setAssets(data);
      setNewAsset({ value: '', asset_type: 'ip', is_internal: false });
    } catch {
      alert('Could not save asset. Check the value and try again.');
    }
  };

  const handleScanAsset = async () => {
    if (!selectedAssetId) return;
    const asset = assets.find(a => a.id.toString() === selectedAssetId);
    if (!asset) return;
    try {
      const res = await axios.post('/api/v1/scan', {
        target: asset.value,
        asset_id: asset.id
      });
      navigate(`/dashboard/${res.data.scan_id}`);
    } catch {
      alert('Error starting scan.');
    }
  };

  const handleStartScan = async () => {
    if (!selectedOrgId) return;
    setNeedsManualIp(false);
    try {
      const res = await axios.post(
        `/api/v1/organizations/${selectedOrgId}/scan/`
      );
      navigate(`/dashboard/${res.data.scan_id}`);
    } catch (err) {
      const detail = err.response?.data?.detail || err.response?.data;
      if (detail.error === 'No assets found') {
        setSuggestions(detail.suggestions || []);
        setNeedsManualIp(true);
      } else {
        alert(detail.message || 'Unexpected error');
      }
    }
  };

  const handleSubmitManualIp = async e => {
    e.preventDefault();
    if (!manualIp) return;
    try {
      await axios.post(
        `/api/v1/organizations/${selectedOrgId}/assets`,
        { value: manualIp, asset_type: 'ip', is_internal: false }
      );
      handleStartScan();
    } catch {
      alert('Could not save asset. Check the IP and try again.');
    }
  };

  const handleScanSelect = e => {
    const scanId = e.target.value;
    if (scanId) navigate(`/dashboard/${scanId}`);
  };

  if (!orgs) return <div>Loading...</div>;

  return (
    <div className="org-dashboard">
      <h2>Organizations</h2>
      <select value={selectedOrgId} onChange={e => setSelectedOrgId(e.target.value)}>
        <option value="">-- select an org --</option>
        {orgs.map(org => <option key={org.id} value={org.id}>{org.name}</option>)}
      </select>

      {selectedOrgId && (
        <>
          <section className="assets-section">
            <h3>Assets</h3>

            <div className="add-asset-form">
              <input
                type="text"
                placeholder="IP or domain"
                value={newAsset.value}
                onChange={e => setNewAsset({ ...newAsset, value: e.target.value })}
              />
              <select
                value={newAsset.asset_type}
                onChange={e => setNewAsset({ ...newAsset, asset_type: e.target.value })}
              >
                <option value="ip">IP</option>
                <option value="domain">Domain</option>
              </select>
              <label>
                Internal?
                <input
                  type="checkbox"
                  checked={newAsset.is_internal}
                  onChange={e => setNewAsset({ ...newAsset, is_internal: e.target.checked })}
                />
              </label>
              <button onClick={handleAddAsset}>Add Asset</button>
            </div>

            {assets.length > 0 && (
              <div className="scan-asset-form">
                <select
                  value={selectedAssetId}
                  onChange={e => setSelectedAssetId(e.target.value)}
                >
                  {assets.map(a => (
                    <option key={a.id} value={a.id}>{a.value}</option>
                  ))}
                </select>
                <button onClick={handleScanAsset}>Scan Asset</button>
              </div>
            )}
          </section>

          {!needsManualIp ? (
            <div className="scan-section">
              {scans.length > 0 ? (
                <>
                  <h3 className="scans-heading">Past Scans</h3>
                  <div className="scans-dropdown-container">
                    <select onChange={handleScanSelect} defaultValue="">
                      <option value="">-- Select a scan --</option>
                      {scans.map(scan => (
                        <option key={scan.scan_id} value={scan.scan_id}>
                          {new Date(scan.scan_time).toLocaleString()} – {scan.target}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="start-scan-button">
                    <button onClick={handleStartScan}>
                      {scans.length ? 'Start New Scan' : 'Start First Scan'}
                    </button>
                  </div>
                </>
              ) : <p>No scans yet.</p>}
            </div>
          ) : (
            <div className="manual-ip-container">
              <p>No assets found automatically. Enter one manually:</p>
              {suggestions.length > 0 && (
                <div className="suggestions">
                  <strong>Suggestions:</strong>{' '}
                  {suggestions.map(ip => (
                    <button key={ip} onClick={() => setManualIp(ip)}>{ip}</button>
                  ))}
                </div>
              )}
              <form onSubmit={handleSubmitManualIp}>
                <input
                  type="text"
                  placeholder="e.g. 8.8.8.8"
                  value={manualIp}
                  onChange={e => setManualIp(e.target.value)}
                  required
                />
                <button type="submit">Save &amp; Scan</button>
              </form>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default OrganizationDashboard;
