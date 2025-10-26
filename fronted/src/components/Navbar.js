import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import BackButton from './BackButton';
import ThemeToggle from './ThemeToggle';
import './Navbar.css';

const Navbar = () => {
  const { pathname } = useLocation();
  const navigate    = useNavigate();
  const token       = localStorage.getItem('access_token');
  const publicPaths = ['/', '/login', '/signup'];
  const showLinks   = token && !publicPaths.includes(pathname);

  // Show back on all but landing
  const showBack = pathname !== '/';

  return (
    <div className="navbar">
      <div className="navbar-left">
        {showBack && <BackButton />}
      </div>
      <div className="navbar-center">
        {showLinks && (
          <>
            <button onClick={() => navigate('/organizations')}>Orgs</button>
            <button onClick={() => navigate('/organizations/new')}>New Org</button>
          </>
        )}
      </div>
      <div className="navbar-right">
        {showLinks && (
          <button
            className="logout"
            onClick={() => {
              localStorage.removeItem('access_token');
              navigate('/login', { replace: true });
            }}
          >
            Logout
          </button>
        )}
        <ThemeToggle />
      </div>
    </div>
  );
};

export default Navbar;