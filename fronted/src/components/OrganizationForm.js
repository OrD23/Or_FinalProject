import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './OrganizationForm.css';

const OrganizationForm = () => {
  const [name, setName] = useState('');
  // start with one blank asset row
  const [assets, setAssets] = useState([
    { value: '', asset_type: 'ip', is_internal: false }
  ]);
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  // handle changes in any asset row
  const handleAssetChange = (idx, field, val) => {
    const updated = [...assets];
    updated[idx][field] = val;
    setAssets(updated);
  };

  const addAssetField = () => {
    setAssets([...assets, { value: '', asset_type: 'ip', is_internal: false }]);
  };

  const removeAssetField = idx => {
    setAssets(assets.filter((_, i) => i !== idx));
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setMessage('');
    try {
      // 1) create the org
      const { data: org } = await axios.post(
        '/api/v1/organizations/create_org',
        { name }
      );
      // 2) create each asset
      for (const asset of assets) {
        if (asset.value.trim()) {
          await axios.post(
            `/api/v1/organizations/${org.id}/assets`,
            asset
          );
        }
      }
      setMessage(`Organization "${org.name}" created with ${assets.length} assets.`);
      // 3) redirect to the org dashboard
      navigate(`/organizations`);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setMessage(typeof detail === 'string' ? detail : 'Error creating organization.');
    }
  };

  return (
    <div className="org-form">
      <h2>Create Organization</h2>
      {message && (
        <p className={message.startsWith('Error') ? 'error' : 'success'}>
          {message}
        </p>
      )}

      <form onSubmit={handleSubmit}>
        <h3>Name</h3>
        <input
          type="text"
          value={name}
          onChange={e => setName(e.target.value)}
          placeholder="e.g. Acme Corp"
          required
        />

        <h3>Assets</h3>
        {assets.map((asset, idx) => (
          <div key={idx} className="asset-row">
            <input
              type="text"
              placeholder="IP or domain"
              value={asset.value}
              onChange={e => handleAssetChange(idx, 'value', e.target.value)}
              required
            />
            <select
              value={asset.asset_type}
              onChange={e => handleAssetChange(idx, 'asset_type', e.target.value)}
            >
              <option value="ip">IP</option>
              <option value="domain">Domain</option>
            </select>
            <label>
              Internal?
              <input
                type="checkbox"
                checked={asset.is_internal}
                onChange={e => handleAssetChange(idx, 'is_internal', e.target.checked)}
              />
            </label>
            {assets.length > 1 && (
              <button type="button" onClick={() => removeAssetField(idx)}>
                Remove
              </button>
            )}
          </div>
        ))}

        <button type="button" onClick={addAssetField} className="add-asset">
          + Add Another Asset
        </button>

        <button type="submit" className="save">
          Save Organization
        </button>
      </form>
    </div>
  );
};

export default OrganizationForm;