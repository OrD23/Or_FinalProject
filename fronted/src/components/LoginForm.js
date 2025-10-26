import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './LoginForm.css';

const LoginForm = () => {
  const [email, setEmail]       = useState('alice@example.com');
  const [password, setPassword] = useState('secret');
  const [error, setError]       = useState('');
  const navigate                = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const response = await axios.post(
        '/api/v1/token',
        new URLSearchParams({ grant_type: 'password', username: email, password }),
        { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
      );
      const token = response.data.access_token;
      localStorage.setItem('access_token', token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      navigate('/search');
    } catch {
      setError('Login failed. Please check your credentials.');
    }
  };

  return (
    <div className="auth-container">
      <h2>Login</h2>
      {error && <p>{error}</p>}
      <form onSubmit={handleLogin}>
        <label>Email:</label>
        <input
          type="text"
          value={email}
          onChange={e => setEmail(e.target.value)}
          placeholder="alice@example.com"
          required
        />
        <label>Password:</label>
        <input
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          placeholder="secret"
          required
        />
        <button type="submit">Log In</button>
      </form>
    </div>
  );
};

export default LoginForm;