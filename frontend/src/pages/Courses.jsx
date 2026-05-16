import React, { useEffect, useState, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import api from '../api';
import { Book, Plus, User, Search } from 'lucide-react';

const Courses = () => {
  const { user } = useContext(AuthContext);
  const [courses, setCourses] = useState([]);
  const [filteredCourses, setFilteredCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  // For Admin creation
  const [showCreate, setShowCreate] = useState(false);
  const [newCourse, setNewCourse] = useState({ courseCode: '', courseName: '', description: '', lecturerId: '' });

  useEffect(() => {
    void fetchCourses();
  }, [user]);

  useEffect(() => {
    const filtered = courses.filter(course => 
      course.courseName.toLowerCase().includes(searchTerm.toLowerCase()) || 
      course.courseCode.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredCourses(filtered);
  }, [searchTerm, courses]);

  const fetchCourses = async () => {
    try {
      let url = '/courses';
      if (user.role === 'student') url = `/courses/student/${user.userId}`;
      if (user.role === 'lecturer') url = `/courses/lecturer/${user.userId}`;

      const res = await api.get(url);
      const data = res.data.courses || [];
      setCourses(data);
      setFilteredCourses(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await api.post('/courses', newCourse);
      setShowCreate(false);
      setNewCourse({ courseCode: '', courseName: '', description: '', lecturerId: '' });
      fetchCourses();
    } catch (err) {
      alert(err.response?.data?.error || 'Error creating course');
    }
  };

  if (loading) return <div className="container animate-in">Loading courses...</div>;

  return (
    <div className="container animate-in">
      <header style={{ marginBottom: '2.5rem' }}>
        <div className="flex-between" style={{ alignItems: 'flex-start' }}>
          <div>
            <h1 style={{ fontSize: '1.875rem', marginBottom: '0.25rem' }}>
              {user.role === 'admin' ? 'All Courses' : 'My Courses'}
            </h1>
            <p style={{ color: 'var(--text-muted)' }}>
              {user.role === 'admin' ? 'Manage and monitor all curriculum offerings.' : 'Access your registered learning materials.'}
            </p>
          </div>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
              <div style={{ position: 'relative' }}>
                <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <input 
                  type="text" 
                  placeholder="Search courses..." 
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  style={{ 
                    paddingLeft: '38px', 
                    width: '280px', 
                    marginBottom: 0,
                    height: '42px'
                  }} 
                />
              </div>
            {user.role === 'admin' && (
              <button className="btn" onClick={() => setShowCreate(!showCreate)}>
                <Plus size={18} /> New Course
              </button>
            )}
          </div>
        </div>
      </header>

      {showCreate && (
        <div className="glass-panel" style={{ marginBottom: '2.5rem' }}>
          <h3 style={{ marginBottom: '1.5rem' }}>Create New Course</h3>
          <form onSubmit={handleCreate} style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1.5rem' }}>
            <div>
              <label>Course Code</label>
              <input 
                type="text" 
                placeholder="e.g. COMP1000"
                value={newCourse.courseCode} 
                onChange={e => setNewCourse({...newCourse, courseCode: e.target.value.toUpperCase()})} 
                required 
              />
            </div>
            <div>
              <label>Course Name</label>
              <input 
                type="text" 
                placeholder="Full Title"
                value={newCourse.courseName} 
                onChange={e => setNewCourse({...newCourse, courseName: e.target.value})} 
                required 
              />
            </div>
            <div style={{ gridColumn: 'span 2' }}>
              <label>Description</label>
              <textarea 
                placeholder="Brief summary of the course..."
                value={newCourse.description} 
                onChange={e => setNewCourse({...newCourse, description: e.target.value})} 
                rows="3"
              />
            </div>
            <div>
              <label>Assign Lecturer ID</label>
              <input 
                type="number" 
                value={newCourse.lecturerId} 
                onChange={e => setNewCourse({...newCourse, lecturerId: e.target.value})} 
                required 
              />
            </div>
            <div style={{ display: 'flex', alignItems: 'flex-end' }}>
              <button type="submit" className="btn" style={{ width: '100%', height: '42px' }}>Create Course</button>
            </div>
          </form>
        </div>
      )}

      <div className="grid">
        {filteredCourses.length === 0 ? (
          <div className="glass-panel" style={{ textAlign: 'center', gridColumn: '1 / -1', padding: '4rem' }}>
            <Book size={48} color="var(--text-muted)" style={{ marginBottom: '1rem', opacity: 0.5 }} />
            <h3>No Courses Found</h3>
            <p>{searchTerm ? `No results for "${searchTerm}"` : 'You are not currently enrolled in any courses.'}</p>
          </div>
        ) : (
          filteredCourses.map(course => (
            <Link to={`/course/${course.courseCode}`} key={course.courseCode} style={{ textDecoration: 'none' }}>
              <div className="glass-panel" style={{ height: '100%', transition: 'all 0.3s ease', cursor: 'pointer' }}>
                <div className="flex-between" style={{ marginBottom: '1.25rem' }}>
                  <div style={{ 
                    background: 'var(--primary-light)', 
                    padding: '0.625rem', 
                    borderRadius: '10px', 
                    color: 'var(--primary)', 
                    display: 'flex' 
                  }}>
                    <Book size={24} />
                  </div>
                  <span style={{ 
                    fontSize: '0.75rem', 
                    background: '#f1f5f9', 
                    padding: '0.25rem 0.625rem', 
                    borderRadius: '20px', 
                    fontWeight: '600',
                    color: 'var(--text-muted)'
                  }}>
                    {course.courseCode}
                  </span>
                </div>
                <h3 style={{ fontSize: '1.125rem', marginBottom: '0.75rem', color: 'var(--text-main)', lineHeight: '1.4' }}>
                  {course.courseName}
                </h3>
                <p style={{ 
                  fontSize: '0.875rem', 
                  marginBottom: '1.5rem',
                  overflow: 'hidden', 
                  textOverflow: 'ellipsis', 
                  display: '-webkit-box', 
                  WebkitLineClamp: 2, 
                  WebkitBoxOrient: 'vertical',
                  minHeight: '2.5rem'
                }}>
                  {course.description || 'Comprehensive study of curriculum objectives.'}
                </p>
                
                {course.lecturerName && (
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '0.5rem', 
                    paddingTop: '1rem', 
                    borderTop: '1px solid var(--border-color)',
                    color: 'var(--text-muted)',
                    fontSize: '0.8125rem'
                  }}>
                    <User size={14} />
                    <span>{course.lecturerName}</span>
                  </div>
                )}
              </div>
            </Link>
          ))
        )}
      </div>
    </div>
  );
};

export default Courses;
