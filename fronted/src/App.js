import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  useLocation,
} from 'react-router-dom';

import Navbar from './components/Navbar';
import LandingPage           from './components/LandingPage';
import LoginForm             from './components/LoginForm';
import SignUpForm            from './components/SignUpForm';
import SearchForm            from './components/SearchForm';
import Dashboard             from './components/Dashboard';
import OrganizationForm      from './components/OrganizationForm';
import OrganizationDashboard from './components/OrganizationDashboard';

const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem('access_token');
  return token ? children : <Navigate to="/login" replace />;
};

function App() {
  const location = useLocation();
  const token    = localStorage.getItem('access_token');
  const publicPaths = ['/', '/login', '/signup'];

  // redirect unauthenticated
  if (!token && !publicPaths.includes(location.pathname)) {
    return <Navigate to="/login" replace />;
  }

  return (
    <>
      {/* single navbar for everything */}
      <Navbar />

      <Routes>
        {/* Public */}
        <Route path="/"       element={<LandingPage />} />
        <Route path="/login"  element={<LoginForm />}   />
        <Route path="/signup" element={<SignUpForm />}  />

        {/* Private */}
        <Route
          path="/organizations"
          element={
            <PrivateRoute>
              <OrganizationDashboard />
            </PrivateRoute>
          }
        />
        <Route
          path="/organizations/new"
          element={
            <PrivateRoute>
              <OrganizationForm />
            </PrivateRoute>
          }
        />
        <Route
          path="/search"
          element={
            <PrivateRoute>
              <SearchForm />
            </PrivateRoute>
          }
        />
        <Route
          path="/dashboard/:scanId"
          element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          }
        />

        {/* Fallback */}
        <Route
          path="*"
          element={
            token
              ? <Navigate to="/organizations" replace />
              : <Navigate to="/" replace />
          }
        />
      </Routes>
    </>
  );
}

export default function RootApp() {
  return (
    <Router>
      <App />
    </Router>
  );
}
