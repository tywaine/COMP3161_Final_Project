import React, { useEffect, useState, useContext } from 'react';
import { useParams, Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import api from '../api';
import { Calendar, MessageSquare, Plus, FileText, Link as LinkIcon, Video, StickyNote, Download, User, Users, CheckCircle, Clock } from 'lucide-react';

const CourseDetail = () => {
  const { courseCode } = useParams();
  const { user } = useContext(AuthContext);
  
  const [activeTab, setActiveTab] = useState('content');
  
  const [course, setCourse] = useState(null);
  const [sections, setSections] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [mySubmissions, setMySubmissions] = useState([]);
  const [forums, setForums] = useState([]);
  const [events, setEvents] = useState([]);
  const [members, setMembers] = useState(null);

  // Forms state
  const [showAddSection, setShowAddSection] = useState(false);
  const [newSectionTitle, setNewSectionTitle] = useState('');
  
  const [showAddItem, setShowAddItem] = useState(null); // sectionId
  const [newItem, setNewItem] = useState({ title: '', contentType: 'file', contentUrl: '', description: '' });

  useEffect(() => {
    if (!courseCode) return;

    void fetchCourseContent();
    void fetchAssignments();
    void fetchForums();
    void fetchEvents();
    void fetchMembers();

    if (user?.role === 'student') {
      void fetchMySubmissions();
    }
}, [courseCode, user]);

  const fetchCourseContent = async () => {
    try {
      const res = await api.get(`/course-content/course/${courseCode}`);
      setCourse(res.data.course);
      setSections(res.data.sections || []);
    } catch (err) { console.error(err); }
  };

  const fetchAssignments = async () => {
    try {
      const res = await api.get(`/assignments/course/${courseCode}`);
      setAssignments(res.data.assignments || []);
    } catch (err) { console.error(err); }
  };

  const fetchMySubmissions = async () => {
    try {
      const res = await api.get(`/assignments/course/${courseCode}/my-submissions`);
      setMySubmissions(res.data.submissions || []);
    } catch (err) { console.error(err); }
  };

  const fetchForums = async () => {
    try {
      const res = await api.get(`/forums/course/${courseCode}`);
      setForums(res.data.forums || []);
    } catch (err) { console.error(err); }
  };

  const fetchEvents = async () => {
    try {
      const res = await api.get(`/calendar-events/course/${courseCode}`);
      setEvents(res.data.events || []);
    } catch (err) { console.error(err); }
  };

  const fetchMembers = async () => {
    try {
      const res = await api.get(`/members/${courseCode}`);
      setMembers(res.data);
    } catch (err) { console.error(err); }
  };

  // Handlers for Lecturer adding content
  const handleAddSection = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/course-content/course/${courseCode}/sections`, { title: newSectionTitle, position: sections.length + 1 });
      setNewSectionTitle('');
      setShowAddSection(false);
      await fetchCourseContent();
    } catch (err) { alert('Failed to add section'); }
  };

  const handleAddItem = async (e, sectionId) => {
    e.preventDefault();
    try {
      await api.post(`/course-content/sections/${sectionId}/items`, newItem);
      setNewItem({ title: '', contentType: 'file', contentUrl: '', description: '' });
      setShowAddItem(null);
      await fetchCourseContent();
    } catch (err) { alert('Failed to add item'); }
  };

  const getIconForType = (type) => {
    switch(type) {
      case 'slide': return <FileText size={18} className="text-blue-500" />;
      case 'link': return <LinkIcon size={18} className="text-green-500" />;
      case 'note': return <StickyNote size={18} className="text-yellow-500" />;
      default: return <Download size={18} className="text-gray-500" />;
    }
  };

  if (!course) return <div className="container">Loading course...</div>;

  const isLecturer = user?.role === 'lecturer';

  return (
    <div className="container animate-in" style={{ paddingBottom: '4rem' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem', color: 'var(--text-main)' }}>{course.courseCode}: {course.courseName}</h1>
        <p style={{ color: 'var(--text-muted)' }}>{course.description}</p>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '1rem', borderBottom: '1px solid var(--border-color)', marginBottom: '2rem' }}>
        {['content', 'assignments', 'grades', 'participants', 'forums', 'calendar'].map(tab => {
          if (tab === 'grades' && isLecturer) return null; // Lecturers might view grades differently
          return (
            <button 
              key={tab}
              onClick={() => setActiveTab(tab)}
              style={{
                background: 'none', border: 'none', padding: '0.75rem 1rem', cursor: 'pointer',
                fontWeight: activeTab === tab ? '600' : '400',
                color: activeTab === tab ? 'var(--primary)' : 'var(--text-muted)',
                borderBottom: activeTab === tab ? '2px solid var(--primary)' : '2px solid transparent',
                textTransform: 'capitalize'
              }}
            >
              {tab}
            </button>
          )
        })}
      </div>

      {/* Content Tab */}
      {activeTab === 'content' && (
        <div className="animate-in">
          {sections.map(section => (
            <div key={section.sectionId} className="glass-panel" style={{ marginBottom: '1.5rem', padding: '1.5rem' }}>
              <h3 style={{ marginBottom: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>{section.title}</h3>
              
              {section.items && section.items.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {section.items.map(item => (
                    <div key={item.sectionItemId} style={{ display: 'flex', alignItems: 'center', gap: '1rem', padding: '0.75rem', background: 'var(--bg-main)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                      <div style={{ padding: '0.5rem', background: 'var(--bg-subtle)', borderRadius: '8px' }}>
                        {getIconForType(item.contentType)}
                      </div>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontWeight: '500' }}>{item.title}</div>
                        {item.description && <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{item.description}</div>}
                      </div>
                      {item.contentUrl && (
                        <a href={item.contentUrl} target="_blank" rel="noreferrer" className="btn" style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}>View Link</a>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No items in this section.</p>
              )}

              {isLecturer && (
                <div style={{ marginTop: '1rem' }}>
                  {showAddItem === section.sectionId ? (
                    <form onSubmit={(e) => handleAddItem(e, section.sectionId)} style={{ background: 'var(--bg-main)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                      <input type="text" placeholder="Item Title" value={newItem.title} onChange={e => setNewItem({...newItem, title: e.target.value})} required style={{ marginBottom: '0.5rem' }} />
                      <select value={newItem.contentType} onChange={e => setNewItem({...newItem, contentType: e.target.value})} style={{ width: '100%', padding: '0.5rem', marginBottom: '0.5rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                        <option value="file">File/Document</option>
                        <option value="link">Web Link (e.g. Zoom)</option>
                        <option value="slide">Presentation Slides</option>
                        <option value="note">Text Note</option>
                      </select>
                      <input type="text" placeholder="URL (if applicable)" value={newItem.contentUrl} onChange={e => setNewItem({...newItem, contentUrl: e.target.value})} style={{ marginBottom: '0.5rem' }} />
                      <input type="text" placeholder="Description (optional)" value={newItem.description} onChange={e => setNewItem({...newItem, description: e.target.value})} style={{ marginBottom: '0.5rem' }} />
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button type="submit" className="btn" style={{ padding: '0.5rem 1rem' }}>Save Item</button>
                        <button type="button" onClick={() => setShowAddItem(null)} className="btn" style={{ background: 'transparent', color: 'var(--text-muted)', border: '1px solid var(--border-color)' }}>Cancel</button>
                      </div>
                    </form>
                  ) : (
                    <button onClick={() => setShowAddItem(section.sectionId)} className="btn" style={{ background: 'var(--primary-light)', color: 'var(--primary)', padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}>
                      <Plus size={14} /> Add Material
                    </button>
                  )}
                </div>
              )}
            </div>
          ))}

          {isLecturer && (
             <div style={{ marginTop: '2rem' }}>
               {showAddSection ? (
                 <form onSubmit={handleAddSection} className="glass-panel" style={{ padding: '1.5rem' }}>
                   <h4>Add New Section</h4>
                   <input type="text" placeholder="Section Title (e.g. Week 1)" value={newSectionTitle} onChange={e => setNewSectionTitle(e.target.value)} required />
                   <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button type="submit" className="btn">Save Section</button>
                      <button type="button" onClick={() => setShowAddSection(false)} className="btn" style={{ background: 'transparent', color: 'var(--text-muted)', border: '1px solid var(--border-color)' }}>Cancel</button>
                   </div>
                 </form>
               ) : (
                 <button onClick={() => setShowAddSection(true)} className="btn">
                   <Plus size={18} /> Add New Section
                 </button>
               )}
             </div>
          )}
        </div>
      )}

      {/* Participants Tab */}
      {activeTab === 'participants' && members && (
        <div className="animate-in grid" style={{ gridTemplateColumns: '1fr' }}>
          <div className="glass-panel" style={{ padding: '1.5rem' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}><User color="var(--primary)" /> Instructor</h3>
            {members.lecturer ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', padding: '1rem', background: 'var(--primary-light)', borderRadius: '12px' }}>
                <div className="user-avatar-small" style={{ width: '40px', height: '40px', fontSize: '1.2rem', background: 'var(--primary)', color: 'white' }}>{members.lecturer.fullName[0]}</div>
                <div>
                  <div style={{ fontWeight: '600', fontSize: '1.1rem' }}>{members.lecturer.fullName}</div>
                  <div style={{ color: 'var(--primary)' }}>{members.lecturer.email}</div>
                </div>
              </div>
            ) : <p>No instructor assigned.</p>}
          </div>

          <div className="glass-panel" style={{ padding: '1.5rem' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}><Users color="var(--primary)" /> Students ({members.students?.length || 0})</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {members.students?.map(s => (
                <div key={s.userId} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.75rem', borderBottom: '1px solid var(--border-color)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <div className="user-avatar-small" style={{ width: '32px', height: '32px' }}>{s.fullName[0]}</div>
                    <div>
                      <div style={{ fontWeight: '500' }}>{s.fullName}</div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{s.email}</div>
                    </div>
                  </div>
                  {isLecturer && s.finalGrade !== null && (
                    <div style={{ fontWeight: '600', color: 'var(--primary)' }}>Grade: {s.finalGrade}%</div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Assignments Tab */}
      {activeTab === 'assignments' && (
        <div className="animate-in">
          {isLecturer && (
            <div style={{ marginBottom: '1.5rem' }}>
               <button className="btn"><Plus size={16}/> Create Assignment</button>
            </div>
          )}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {assignments.length === 0 ? <p>No assignments.</p> : assignments.map(a => {
              const submission = mySubmissions.find(sub => sub.assignmentId === a.assignmentId);
              return (
                <div key={a.assignmentId} className="glass-panel flex-between" style={{ padding: '1.5rem' }}>
                  <div>
                    <h4 style={{ fontSize: '1.2rem', marginBottom: '0.25rem' }}>{a.title}</h4>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '0.5rem' }}>{a.description}</p>
                    <div style={{ display: 'flex', gap: '1rem', fontSize: '0.8rem', color: 'var(--text-main)' }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}><Clock size={14} className="text-orange-500" /> Due: {a.dueDate}</span>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}><CheckCircle size={14} className="text-green-500" /> Marks: {a.totalMarks}</span>
                    </div>
                  </div>
                  {!isLecturer && (
                    <div style={{ textAlign: 'right' }}>
                      {submission ? (
                        <div>
                          <div style={{ color: 'var(--primary)', fontWeight: 'bold' }}>{submission.grade !== null ? `${submission.grade} / ${a.totalMarks}` : 'Pending Grade'}</div>
                          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Submitted</div>
                        </div>
                      ) : (
                        <button className="btn" style={{ padding: '0.5rem 1rem', fontSize: '0.8rem' }}>Submit Work</button>
                      )}
                    </div>
                  )}
                  {isLecturer && (
                    <button className="btn" style={{ padding: '0.5rem 1rem', fontSize: '0.8rem' }}>View Submissions</button>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Grades Tab (Student Only) */}
      {activeTab === 'grades' && (
        <div className="animate-in glass-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ marginBottom: '1.5rem' }}>My Grades</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid var(--border-color)', textAlign: 'left' }}>
                <th style={{ padding: '0.75rem 0' }}>Assignment</th>
                <th style={{ padding: '0.75rem 0' }}>Status</th>
                <th style={{ padding: '0.75rem 0' }}>Grade</th>
                <th style={{ padding: '0.75rem 0' }}>Feedback</th>
              </tr>
            </thead>
            <tbody>
              {assignments.map(a => {
                const sub = mySubmissions.find(s => s.assignmentId === a.assignmentId);
                return (
                  <tr key={a.assignmentId} style={{ borderBottom: '1px solid var(--border-color)' }}>
                    <td style={{ padding: '1rem 0', fontWeight: '500' }}>{a.title}</td>
                    <td style={{ padding: '1rem 0' }}>
                      {sub ? <span style={{ color: '#10b981', background: '#d1fae5', padding: '0.25rem 0.5rem', borderRadius: '4px', fontSize: '0.8rem' }}>Submitted</span> : <span style={{ color: '#ef4444', background: '#fee2e2', padding: '0.25rem 0.5rem', borderRadius: '4px', fontSize: '0.8rem' }}>Missing</span>}
                    </td>
                    <td style={{ padding: '1rem 0', fontWeight: 'bold' }}>
                      {sub?.grade !== null && sub?.grade !== undefined ? `${sub.grade} / ${a.totalMarks}` : '-'}
                    </td>
                    <td style={{ padding: '1rem 0', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                      {sub?.feedback || '-'}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
          
          <div style={{ marginTop: '2rem', padding: '1.5rem', background: 'var(--primary-light)', borderRadius: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ fontWeight: '600', fontSize: '1.2rem' }}>Course Final Grade</div>
            <div style={{ fontWeight: '800', fontSize: '1.5rem', color: 'var(--primary)' }}>
              {members?.students?.find(s => s.userId === user.userId)?.finalGrade || 'N/A'}%
            </div>
          </div>
        </div>
      )}

      {/* Forums Tab */}
      {activeTab === 'forums' && (
        <div className="animate-in grid" style={{ gridTemplateColumns: '1fr' }}>
          <div className="glass-panel" style={{ padding: '1.5rem' }}>
             <div className="flex-between" style={{ marginBottom: '1.5rem' }}>
               <h3>Discussion Forums</h3>
             </div>
             <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
               {forums.length === 0 ? <p>No forums yet.</p> : forums.map(f => (
                 <Link to={`/forum/${f.forumId}`} key={f.forumId} style={{ textDecoration: 'none' }}>
                   <div style={{ padding: '1rem', border: '1px solid var(--border-color)', borderRadius: '12px', background: 'var(--bg-main)', transition: 'all 0.2s' }}
                        onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--primary)'}
                        onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border-color)'}>
                     <h4 style={{ color: 'var(--text-main)' }}>{f.title}</h4>
                   </div>
                 </Link>
               ))}
             </div>
          </div>
        </div>
      )}

      {/* Calendar Tab */}
      {activeTab === 'calendar' && (
        <div className="animate-in grid" style={{ gridTemplateColumns: '1fr' }}>
          <div className="glass-panel" style={{ padding: '1.5rem' }}>
             <h3 style={{ marginBottom: '1.5rem' }}>Upcoming Events</h3>
             <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
               {events.length === 0 ? <p>No events scheduled.</p> : events.map(e => (
                 <div key={e.eventId} style={{ padding: '1rem', borderLeft: '4px solid #10b981', background: 'var(--bg-main)', borderRadius: '8px' }}>
                   <h4>{e.title}</h4>
                   <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>{e.eventDateTime}</p>
                 </div>
               ))}
             </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default CourseDetail;
