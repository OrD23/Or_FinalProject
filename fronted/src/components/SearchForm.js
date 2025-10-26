// frontend/src/components/SearchForm.js
import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './SearchForm.css';

const SearchForm = () => {
  const [target, setTarget]   = useState('');
  const [loading, setLoading] = useState(false);
  const navigate              = useNavigate();

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post('/api/v1/scan/', { target });
      const scanId = response.data.scan_id;
      navigate(`/dashboard/${scanId}`);
    } catch (err) {
      console.error('Scan error:', err);
      alert('Error initiating scan');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="search-wrapper">
      <form onSubmit={handleSearch}>
        <input
          type="text"
          value={target}
          onChange={e => setTarget(e.target.value)}
          placeholder="Enter domain or IP"
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Scanning...' : 'Search'}
        </button>
      </form>
    </div>
  );
};

export default SearchForm;