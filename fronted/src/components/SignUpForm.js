import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './SignUpForm.css';

const SignUpForm = () => {
  const [name, setName]         = useState('');
  const [email, setEmail]       = useState('');
  const [password, setPassword] = useState('');
  const [error, setError]       = useState('');
  const navigate                = useNavigate();

  const handleSignUp = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await axios.post('/api/v1/signup', { name, email, password });
      alert('User created successfully. Please log in.');
      navigate('/login');
    } catch (err) {
      setError(err.response?.data?.detail || 'Sign up failed.');
    }
  };

  return (
    <div className="signup-wrapper">
      <div className="signup-card">
        <h2 className="signup-title">Sign Up</h2>
        {error && <p className="signup-error">{error}</p>}
        <form onSubmit={handleSignUp}>
          <div className="signup-field">
            <label>Name:</label>
            <input
              className="signup-input"
              type="text"
              value={name}
              onChange={e => setName(e.target.value)}
              required
            />
          </div>
          <div className="signup-field">
            <label>Email:</label>
            <input
              className="signup-input"
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="signup-field">
            <label>Password:</label>
            <input
              className="signup-input"
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="signup-button">
            Sign Up
          </button>
        </form>
      </div>
    </div>
  );
};

export default SignUpForm;
