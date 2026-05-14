import React, { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { LogOut, BookOpen } from 'lucide-react';

const Navbar = () => {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', textDecoration: 'none', color: 'var(--text-main)' }}>
        <div style={{ background: 'var(--primary)', color: 'white', padding: '0.5rem', borderRadius: 'var(--radius-sm)', display: 'flex' }}>
          <BookOpen size={24} />
        </div>
        <span style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>OURVLE</span>
      </Link>
      
      {user && (
        <div className="nav-links">
          <Link to="/">Courses</Link>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginLeft: '1rem', borderLeft: '1px solid var(--border-color)', paddingLeft: '1rem' }}>
            <span style={{ fontSize: '0.875rem' }}>
              <span style={{ color: 'var(--text-muted)' }}>Logged in as </span>
              <strong>{user.fullName}</strong>
            </span>
            <button onClick={handleLogout} className="btn btn-secondary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.875rem' }}>
              <LogOut size={16} /> Logout
            </button>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
