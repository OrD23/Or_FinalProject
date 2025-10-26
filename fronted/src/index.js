// src/index.js
import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './index.css';
import './styles/theme.css';
import { ThemeProvider } from './ThemeContext';

import axios from 'axios';

// base URL
axios.defaults.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// ——— attach JWT to every request ———
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

const container = document.getElementById('root');
const root = createRoot(container);

root.render(
  <React.StrictMode>
    <ThemeProvider>
      <App />
    </ThemeProvider>
  </React.StrictMode>
);
