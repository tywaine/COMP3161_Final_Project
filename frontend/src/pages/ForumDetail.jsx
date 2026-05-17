import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../api';
import { MessageCircle, Plus } from 'lucide-react';

const ForumDetail = () => {
  const { forumId } = useParams();
  const [threads, setThreads] = useState([]);
  
  const [newThread, setNewThread] = useState({ title: '', content: '' });
  const [showCreate, setShowCreate] = useState(false);

  useEffect(() => {
    fetchThreads();
  }, [forumId]);

    const fetchThreads = async () => {
    try {
      const res = await api.get(`/discussion-threads/forum/${forumId}`);
      setThreads(res.data.threads || []);
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreateThread = async (e) => {
    e.preventDefault();

    try {
      await api.post(`/discussion-threads/forum/${forumId}`, newThread);
      setNewThread({ title: '', content: '' });
      setShowCreate(false);
      await fetchThreads();
    } catch (err) {
      alert('Failed to create thread');
      console.error(err);
    }
  };

  return (
    <div className="container animate-in">
      <div className="flex-between" style={{ marginBottom: '2rem' }}>
        <h2>Forum Threads</h2>
        <button className="btn" onClick={() => setShowCreate(!showCreate)}>
          <Plus size={18} /> New Thread
        </button>
      </div>

      {showCreate && (
        <form onSubmit={handleCreateThread} className="glass-panel" style={{ marginBottom: '2rem' }}>
          <input 
            type="text" 
            placeholder="Thread Title" 
            value={newThread.title} 
            onChange={e => setNewThread({...newThread, title: e.target.value})} 
            required 
          />
          <textarea 
            placeholder="Initial Post Content..." 
            value={newThread.content} 
            onChange={e => setNewThread({...newThread, content: e.target.value})} 
            required 
            rows={4}
          />
          <button type="submit" className="btn">Post Thread</button>
        </form>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {threads.length === 0 ? <p>No threads in this forum yet. Be the first!</p> : threads.map(t => (
          <Link to={`/thread/${t.threadId}`} key={t.threadId} style={{ textDecoration: 'none' }}>
            <div className="glass-panel" style={{ padding: '1.5rem', transition: 'var(--transition)' }}
                 onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-subtle)'}
                 onMouseLeave={e => e.currentTarget.style.background = 'white'}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
                <MessageCircle color="var(--primary)" size={24} style={{ marginTop: '0.2rem' }} />
                <div>
                  <h3 style={{ color: 'var(--text-main)', marginBottom: '0.25rem' }}>{t.title}</h3>
                  <small style={{ color: 'var(--text-muted)' }}>Created on: {new Date(t.createdAt).toLocaleString()}</small>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default ForumDetail;
