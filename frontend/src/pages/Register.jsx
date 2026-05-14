import React, { useState, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { UserPlus } from 'lucide-react';

const Register = () => {
  const [formData, setFormData] = useState({
    userId: '',
    fullName: '',
    email: '',
    password: '',
    role: 'student',
    department: ''
  });
  const [error, setError] = useState('');
  const { register } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await register(formData);
      navigate('/login');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to register');
    }
  };

  return (
    <div className="container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '80vh' }}>
      <div className="glass-panel animate-in" style={{ width: '100%', maxWidth: '500px' }}>
        <h2 style={{ textAlign: 'center', marginBottom: '2rem' }}>Create Account</h2>
        {error && <p className="error-text">{error}</p>}
        <form onSubmit={handleSubmit}>
          <div className="flex-between" style={{ gap: '1rem' }}>
            <div style={{ flex: 1 }}>
              <label>User ID</label>
              <input type="number" name="userId" onChange={handleChange} required />
            </div>
            <div style={{ flex: 1 }}>
              <label>Role</label>
              <select name="role" onChange={handleChange} value={formData.role}>
                <option value="student">Student</option>
                <option value="lecturer">Lecturer</option>
                <option value="admin">Admin</option>
              </select>
            </div>
          </div>
          <div>
            <label>Full Name</label>
            <input type="text" name="fullName" onChange={handleChange} required />
          </div>
          <div>
            <label>Email Address</label>
            <input type="email" name="email" onChange={handleChange} required />
          </div>
          {formData.role === 'lecturer' && (
            <div>
              <label>Department</label>
              <input type="text" name="department" onChange={handleChange} required />
            </div>
          )}
          <div>
            <label>Password</label>
            <input type="password" name="password" onChange={handleChange} required />
          </div>
          
          <button type="submit" className="btn" style={{ width: '100%', marginTop: '1rem' }}>
            <UserPlus size={18} /> Register
          </button>
        </form>
        <p style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.875rem' }}>
          Already have an account? <Link to="/login" style={{ color: 'var(--primary)' }}>Login</Link>
        </p>
      </div>
    </div>
  );
};

export default Register;
