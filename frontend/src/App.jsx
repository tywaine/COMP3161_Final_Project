import React, { useContext } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, AuthContext } from './context/AuthContext';
import Sidebar from './components/Sidebar';
import Breadcrumbs from './components/Breadcrumbs';
import Login from './pages/Login';
import Register from './pages/Register';

// Pages
import Courses from './pages/Courses';
import CourseDetail from './pages/CourseDetail';
import ForumDetail from './pages/ForumDetail';
import ThreadDetail from './pages/ThreadDetail';

const PrivateRoute = ({ children }) => {
  const { user, loading } = useContext(AuthContext);
  if (loading) return <div className="container">Loading...</div>;
  return user ? children : <Navigate to="/login" />;
};

const AppRoutes = () => {
  const { user } = useContext(AuthContext);

  return (
    <div className={user ? "app-layout" : ""} data-role={user?.role}>
      {user && <Sidebar />}
      <main className={user ? "main-content" : ""}>
        {user && <Breadcrumbs />}
        <Routes>
          <Route path="/login" element={!user ? <Login /> : <Navigate to="/" />} />
          <Route path="/register" element={!user ? <Register /> : <Navigate to="/" />} />
          
          <Route path="/" element={<PrivateRoute><Courses /></PrivateRoute>} />
          <Route path="/courses" element={<PrivateRoute><Courses /></PrivateRoute>} />
          <Route path="/course/:courseId" element={<PrivateRoute><CourseDetail /></PrivateRoute>} />
          <Route path="/forum" element={<PrivateRoute><div className="container animate-in"><h2>Forums</h2><p>Select a course to view its forum.</p></div></PrivateRoute>} />
          <Route path="/forum/:forumId" element={<PrivateRoute><ForumDetail /></PrivateRoute>} />
          <Route path="/thread/:threadId" element={<PrivateRoute><ThreadDetail /></PrivateRoute>} />
          <Route path="/calendar" element={<PrivateRoute><div className="container animate-in"><h2>Calendar</h2><p>Coming soon...</p></div></PrivateRoute>} />
          
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </main>
    </div>
  );
};

const App = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
