import React from 'react';
import { useNavigate } from 'react-router-dom';
import './LandingPage.css';

const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="landing-container">
      <h1>Welcome to Shield Scan</h1>
      <div>
        <button onClick={() => navigate('/login')}>Login</button>
        <button onClick={() => navigate('/signup')}>Sign Up</button>
      </div>
    </div>
  );
};

export default LandingPage;