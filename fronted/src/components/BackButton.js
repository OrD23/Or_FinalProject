import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './BackButton.css';

const BackButton = () => {
  const navigate = useNavigate();
  const { pathname } = useLocation();

  const handleBack = () => {
    // On login/signup pages, go back to landing
    if (pathname === '/login' || pathname === '/signup') {
      navigate('/', { replace: true });
    } else {
      navigate(-1);
    }
  };

  return (
    <button className="back-button" onClick={handleBack}>
      ← Back
    </button>
  );
};

export default BackButton;