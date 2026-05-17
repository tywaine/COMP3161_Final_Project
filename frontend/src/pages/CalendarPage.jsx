import React, { useContext, useState } from 'react';
import { AuthContext } from '../context/AuthContext';
import api from '../api';
import { Calendar as CalendarIcon, Search } from 'lucide-react';

const CalendarPage = () => {
  const { user } = useContext(AuthContext);

  const today = new Date().toISOString().split('T')[0];

  const [selectedDate, setSelectedDate] = useState(today);
  const [events, setEvents] = useState([]);
  const [searched, setSearched] = useState(false);
  const [loading, setLoading] = useState(false);

  const fetchEventsByDate = async (e) => {
    e.preventDefault();

    if (user?.role !== 'student') {
      alert('This calendar search is for students.');
      return;
    }

    try {
      setLoading(true);
      setSearched(true);

      const res = await api.get(`/calendar-events/student/${user.userId}?date=${selectedDate}`);
      setEvents(res.data.events || []);
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.message || err.response?.data?.error || 'Failed to load calendar events');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container animate-in">
      <header style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.875rem', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <CalendarIcon color="var(--primary)" /> Calendar
        </h1>
        <p style={{ color: 'var(--text-muted)' }}>
          Search course calendar events by date.
        </p>
      </header>

      {user?.role !== 'student' ? (
        <div className="glass-panel" style={{ padding: '2rem' }}>
          <h3>Calendar Search</h3>
          <p style={{ color: 'var(--text-muted)' }}>
            The date-based calendar endpoint is designed for students. Lecturers and admins can view course events inside each course page.
          </p>
        </div>
      ) : (
        <>
          <form
            onSubmit={fetchEventsByDate}
            className="glass-panel"
            style={{
              padding: '1.5rem',
              marginBottom: '2rem',
              display: 'flex',
              gap: '1rem',
              alignItems: 'flex-end',
              flexWrap: 'wrap'
            }}
          >
            <div>
              <label>Select Date</label>
              <input
                type="date"
                value={selectedDate}
                onChange={e => setSelectedDate(e.target.value)}
                required
                style={{ marginBottom: 0 }}
              />
            </div>

            <button type="submit" className="btn" style={{ height: '42px' }}>
              <Search size={16} /> Search Events
            </button>
          </form>

          <div className="glass-panel" style={{ padding: '1.5rem' }}>
            <h3 style={{ marginBottom: '1.5rem' }}>Events for {selectedDate}</h3>

            {loading ? (
              <p>Loading events...</p>
            ) : !searched ? (
              <p style={{ color: 'var(--text-muted)' }}>Choose a date to view your events.</p>
            ) : events.length === 0 ? (
              <p style={{ color: 'var(--text-muted)' }}>No events found for this date.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {events.map(event => (
                  <div
                    key={event.eventId}
                    style={{
                      padding: '1rem',
                      borderLeft: '4px solid #10b981',
                      background: 'var(--bg-main)',
                      borderRadius: '8px'
                    }}
                  >
                    <h4>{event.title}</h4>
                    <p style={{ fontSize: '0.85rem', color: 'var(--primary)', fontWeight: '600' }}>
                      {event.courseCode} {event.courseName ? `- ${event.courseName}` : ''}
                    </p>

                    {event.description && (
                      <p style={{ color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                        {event.description}
                      </p>
                    )}

                    <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                      {event.eventDateTime}
                    </p>

                    {event.createdByName && (
                      <small style={{ color: 'var(--text-muted)' }}>
                        Created by {event.createdByName}
                      </small>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default CalendarPage;