import React, { useContext, useEffect, useState } from 'react';
import { AuthContext } from '../context/AuthContext';
import api from '../api';
import { BarChart3 } from 'lucide-react';

const Reports = () => {
  const { user } = useContext(AuthContext);

  const [activeReport, setActiveReport] = useState('courses-50-or-more-students');
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);

  const reportOptions = [
    {
      key: 'courses-50-or-more-students',
      title: 'Courses With 50+ Students'
    },
    {
      key: 'students-5-or-more-courses',
      title: 'Students With 5+ Courses'
    },
    {
      key: 'lecturers-3-or-more-courses',
      title: 'Lecturers With 3+ Courses'
    },
    {
      key: 'top-10-most-enrolled-courses',
      title: 'Top 10 Most Enrolled Courses'
    },
    {
      key: 'top-10-students-highest-overall-averages',
      title: 'Top 10 Student Averages'
    }
  ];

  useEffect(() => {
    if (user?.role === 'admin') {
      void fetchReport(activeReport);
    }
  }, [activeReport, user]);

  const fetchReport = async (reportKey) => {
    try {
      setLoading(true);
      const res = await api.get(`/reports/${reportKey}`);
      setReports(res.data.reports || []);
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.message || err.response?.data?.error || 'Failed to load report');
    } finally {
      setLoading(false);
    }
  };

  const getColumns = () => {
    if (reports.length === 0) return [];
    return Object.keys(reports[0]);
  };

  if (user?.role !== 'admin') {
    return (
      <div className="container animate-in">
        <div className="glass-panel" style={{ padding: '2rem' }}>
          <h2>Access Denied</h2>
          <p style={{ color: 'var(--text-muted)' }}>Only admins can view reports.</p>
        </div>
      </div>
    );
  }

  const columns = getColumns();

  return (
    <div className="container animate-in">
      <header style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.875rem', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <BarChart3 color="var(--primary)" /> Reports
        </h1>
        <p style={{ color: 'var(--text-muted)' }}>
          View database report summaries
        </p>
      </header>

      <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', marginBottom: '2rem' }}>
        {reportOptions.map(option => (
          <button
            key={option.key}
            onClick={() => setActiveReport(option.key)}
            className="btn"
            style={{
              background: activeReport === option.key ? 'var(--primary)' : 'var(--bg-subtle)',
              color: activeReport === option.key ? 'white' : 'var(--text-main)',
              border: '1px solid var(--border-color)'
            }}
          >
            {option.title}
          </button>
        ))}
      </div>

      <div className="glass-panel" style={{ padding: '1.5rem', overflowX: 'auto' }}>
        <h3 style={{ marginBottom: '1.5rem' }}>
          {reportOptions.find(r => r.key === activeReport)?.title}
        </h3>

        {loading ? (
          <p>Loading report...</p>
        ) : reports.length === 0 ? (
          <p style={{ color: 'var(--text-muted)' }}>No results for this report.</p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid var(--border-color)', textAlign: 'left' }}>
                {columns.map(column => (
                  <th key={column} style={{ padding: '0.75rem' }}>
                    {column}
                  </th>
                ))}
              </tr>
            </thead>

            <tbody>
              {reports.map((row, index) => (
                <tr key={index} style={{ borderBottom: '1px solid var(--border-color)' }}>
                  {columns.map(column => (
                    <td key={column} style={{ padding: '0.75rem' }}>
                      {row[column] ?? '-'}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default Reports;