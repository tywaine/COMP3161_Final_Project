import React, { useEffect, useState, useContext } from 'react';
import { useParams, Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import api from '../api';
import { CornerDownRight, MessageSquare } from 'lucide-react';

const ThreadDetail = () => {
  const { threadId } = useParams();
  const { user } = useContext(AuthContext);
  const [thread, setThread] = useState(null);
  const [posts, setPosts] = useState([]);
  const [replyContent, setReplyContent] = useState('');
  const [replyingTo, setReplyingTo] = useState(null); // parentPostId

  useEffect(() => {
    fetchPosts();
  }, [threadId]);

  const fetchPosts = async () => {
    try {
      const res = await api.get(`/discussion-threads/${threadId}/posts`);
      const threadData = res.data.thread;
      const postsData = res.data.posts || [];
      
      setThread(threadData);
      setPosts(postsData);

      // Save to recent threads
      if (user && threadData) {
        const key = `recentThreads_${user.userId}`;
        const recent = JSON.parse(localStorage.getItem(key) || '[]');
        const updated = [
          { threadId, title: threadData.threadTitle },
          ...recent.filter(t => t.threadId !== threadId)
        ].slice(0, 3);
        localStorage.setItem(key, JSON.stringify(updated));
        
        // Dispatch event so Sidebar can update if it's already mounted
        window.dispatchEvent(new Event('recentThreadsUpdated'));
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleReply = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/discussion-threads/${threadId}/reply`, { 
        content: replyContent,
        parentPostId: replyingTo
      });
      setReplyContent('');
      setReplyingTo(null);
      fetchPosts();
    } catch (err) {
      alert('Failed to post reply');
    }
  };

  // Helper to build nested tree
  const buildPostTree = () => {
    const map = {};
    const roots = [];
    posts.forEach(post => {
      map[post.postId] = { ...post, children: [] };
    });
    posts.forEach(post => {
      if (post.parentPostId) {
        if (map[post.parentPostId]) {
          map[post.parentPostId].children.push(map[post.postId]);
        }
      } else {
        roots.push(map[post.postId]);
      }
    });
    return roots;
  };

  const renderPostNode = (node, depth = 0) => {
    return (
      <div key={node.postId} style={{ marginLeft: depth > 0 ? 'min(2rem, 5vw)' : '0', marginTop: '1rem' }}>
        <div className="glass-panel animate-in" style={{ padding: '1.25rem', borderLeft: depth > 0 ? '2px solid var(--primary)' : 'none' }}>
          <div className="flex-between" style={{ marginBottom: '0.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <div className="user-avatar-small" style={{ width: '24px', height: '24px', fontSize: '0.6rem' }}>
                {node.fullName?.[0] || 'U'}
              </div>
              <strong style={{ color: 'var(--text-main)', fontSize: '0.9rem' }}>
                {node.fullName}
              </strong>
            </div>
            <small style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
              {node.createdAt}
            </small>
          </div>
          <p style={{ color: 'var(--text-main)', marginBottom: '1rem', whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>
            {node.content}
          </p>
          
          <button 
            className="btn" 
            style={{ 
              padding: '0.3rem 0.75rem', 
              fontSize: '0.75rem', 
              background: 'var(--bg-subtle)', 
              color: 'var(--primary)',
              borderRadius: '8px'
            }}
            onClick={() => setReplyingTo(replyingTo === node.postId ? null : node.postId)}
          >
            <CornerDownRight size={12} /> Reply
          </button>

          {replyingTo === node.postId && (
            <form onSubmit={handleReply} style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem' }}>
              <input 
                type="text" 
                placeholder={`Reply to ${node.fullName}...`} 
                value={replyContent} 
                onChange={e => setReplyContent(e.target.value)} 
                autoFocus
                required 
                style={{ marginBottom: 0, height: '38px', fontSize: '0.875rem' }}
              />
              <button type="submit" className="btn" style={{ height: '38px', padding: '0 1rem' }}>Send</button>
            </form>
          )}
        </div>
        
        {/* Render children recursively */}
        {node.children && node.children.map(child => renderPostNode(child, depth + 1))}
      </div>
    );
  };

  return (
    <div className="animate-in">
      <div style={{ marginBottom: '2.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
          <div style={{ 
            background: 'var(--primary-light)', 
            padding: '0.5rem', 
            borderRadius: '10px', 
            color: 'var(--primary)' 
          }}>
            <MessageSquare size={24} />
          </div>
          <div>
            <h1 style={{ fontSize: '1.75rem', marginBottom: '0.25rem' }}>
              {thread?.threadTitle || 'Loading Thread...'}
            </h1>
            <p style={{ color: 'var(--text-muted)' }}>Discussion started on {thread?.createdAt || '...'}</p>
          </div>
        </div>
      </div>

      <div style={{ marginBottom: '3rem' }}>
        {posts.length === 0 ? (
          <div className="glass-panel" style={{ textAlign: 'center', padding: '3rem' }}>
            <p style={{ color: 'var(--text-muted)' }}>No posts in this thread yet.</p>
          </div>
        ) : (
          buildPostTree().map(root => renderPostNode(root, 0))
        )}
      </div>

      {/* Main Reply Box (root level) */}
      <div className="glass-panel" style={{ marginTop: '2rem' }}>
        <h4 style={{ marginBottom: '1rem' }}>Add a Post</h4>
        <form onSubmit={handleReply}>
          <textarea 
            placeholder="What are your thoughts?" 
            value={replyingTo === null ? replyContent : ''} 
            onChange={e => {
              setReplyingTo(null);
              setReplyContent(e.target.value);
            }} 
            required 
            rows={4}
            style={{ minHeight: '120px' }}
          />
          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button type="submit" className="btn">Post to Thread</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ThreadDetail;
