import React, { useContext, useEffect, useState } from 'react';
import { NavLink, Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import {
  Home,
  BookOpen,
  MessageSquare,
  Calendar as CalendarIcon,
  LogOut,
  ChevronLeft,
  ChevronRight,
  History,
  BarChart3
} from 'lucide-react';
import api from '../api';

const Sidebar = () => {
  const { user, logout } = useContext(AuthContext);

  const [deadlines, setDeadlines] = useState([]);
  const [events, setEvents] = useState([]);
  const [recentThreads, setRecentThreads] = useState([]);
  const [currentDate, setCurrentDate] = useState(new Date());

  useEffect(() => {
    if (user) {
      fetchUpcoming();
      loadRecentThreads();

      const handleUpdate = () => loadRecentThreads();
      window.addEventListener('recentThreadsUpdated', handleUpdate);

      return () => window.removeEventListener('recentThreadsUpdated', handleUpdate);
    }
  }, [user]);

  const fetchUpcoming = async () => {
    try {
      const [assignRes, eventRes] = await Promise.all([
        api.get('/assignments/upcoming'),
        api.get('/calendar-events/upcoming')
      ]);

      setDeadlines(assignRes.data.assignments || []);
      setEvents(eventRes.data.events || []);
    } catch (err) {
      console.error('Failed to fetch upcoming items', err);
    }
  };

  const loadRecentThreads = () => {
    if (!user) return;

    const saved = JSON.parse(localStorage.getItem(`recentThreads_${user.userId}`) || '[]');
    setRecentThreads(saved);
  };

  const navItems = [
    { name: 'Dashboard', path: '/', icon: <Home size={20} /> },
    { name: 'Courses', path: '/courses', icon: <BookOpen size={20} /> },
    { name: 'Forum', path: '/forum', icon: <MessageSquare size={20} /> },
    { name: 'Calendar', path: '/calendar', icon: <CalendarIcon size={20} /> },
    ...(user?.role === 'admin'
      ? [{ name: 'Reports', path: '/reports', icon: <BarChart3 size={20} /> }]
      : [])
  ];

  const daysInMonth = (year, month) => new Date(year, month + 1, 0).getDate();
  const firstDayOfMonth = (year, month) => new Date(year, month, 1).getDay();

  const renderCalendar = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    const days = daysInMonth(year, month);
    const startDay = firstDayOfMonth(year, month);

    const monthNames = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];

    const prevMonth = () => setCurrentDate(new Date(year, month - 1, 1));
    const nextMonth = () => setCurrentDate(new Date(year, month + 1, 1));

    const busyDays = {};

    deadlines.forEach(d => {
      if (!d.dueDate) return;
      const date = d.dueDate.split(' ')[0];
      busyDays[date] = 'deadline';
    });

    events.forEach(e => {
      if (!e.eventDateTime) return;
      const date = e.eventDateTime.split(' ')[0];
      if (!busyDays[date]) busyDays[date] = 'event';
    });

    const calendarGrid = [];

    for (let i = 0; i < startDay; i++) {
      calendarGrid.push(<div key={`empty-${i}`} className="calendar-day empty"></div>);
    }

    for (let i = 1; i <= days; i++) {
      const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`;
      const status = busyDays[dateStr];

      calendarGrid.push(
        <div
          key={i}
          className={`calendar-day ${status ? `has-item ${status}` : ''}`}
          title={status ? (status === 'deadline' ? 'Deadline' : 'Event') : ''}
        >
          {i}
        </div>
      );
    }

    return (
      <div className="mini-calendar">
        <div className="calendar-header">
          <span>{monthNames[month]} {year}</span>

          <div className="calendar-nav">
            <button onClick={prevMonth}><ChevronLeft size={14} /></button>
            <button onClick={nextMonth}><ChevronRight size={14} /></button>
          </div>
        </div>

        <div className="calendar-weekdays">
          {['S', 'M', 'T', 'W', 'T', 'F', 'S'].map(d => <div key={d}>{d}</div>)}
        </div>

        <div className="calendar-grid">
          {calendarGrid}
        </div>
      </div>
    );
  };

  return (
    <aside className="sidebar">
      <div style={{ padding: '2rem 1.25rem', flex: 1, overflowY: 'auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2.5rem' }}>
          <div className="logo-box">
            PLE
          </div>

          <div>
            <div
              style={{
                fontWeight: '800',
                fontSize: '1.25rem',
                letterSpacing: '-0.02em',
                color: 'var(--text-main)',
                lineHeight: 1
              }}
            >
              Pelican
            </div>

            <div
              style={{
                fontSize: '0.75rem',
                fontWeight: '500',
                color: 'var(--text-muted)',
                letterSpacing: '0.05em'
              }}
            >
              LEARNING ENV.
            </div>
          </div>
        </div>

        <nav>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            {navItems.map((item) => (
              <li key={item.name} style={{ marginBottom: '0.75rem' }}>
                <NavLink
                  to={item.path}
                  className={({ isActive }) =>
                    isActive ? 'nav-link active glassy-text' : 'nav-link glassy-text'
                  }
                >
                  <span className="icon-wrapper">{item.icon}</span>
                  {item.name}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        <div style={{ marginTop: '2.5rem' }}>
          <h5 className="sidebar-label">Activity Calendar</h5>

          {renderCalendar()}

          <div style={{ marginTop: '0.75rem', display: 'flex', gap: '1rem', fontSize: '0.65rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
              <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#f59e0b' }}></div>
              <span>Deadline</span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
              <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981' }}></div>
              <span>Event</span>
            </div>
          </div>
        </div>

        {recentThreads.length > 0 && (
          <div style={{ marginTop: '2.5rem' }}>
            <h5 className="sidebar-label">Recently Viewed</h5>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {recentThreads.map((t, idx) => (
                <Link key={idx} to={`/thread/${t.threadId}`} className="recent-thread-link">
                  <History size={14} style={{ opacity: 0.5, flexShrink: 0 }} />
                  <span style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {t.title}
                  </span>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="sidebar-footer">
        <div className="user-profile-compact">
          <div className="user-avatar-small">
            {user.fullName?.[0] || 'U'}
          </div>

          <div className="user-info-text">
            <div className="user-name-small">{user.fullName}</div>
            <div className="user-role-small">{user.role}</div>
          </div>
        </div>

        <button onClick={logout} className="logout-btn-minimal">
          <LogOut size={16} /> Logout
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;