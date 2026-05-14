import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';

const Breadcrumbs = () => {
  const location = useLocation();
  const pathnames = location.pathname.split('/').filter((x) => x);

  // Map path segments to readable names if needed
  const segmentMap = {
    'course': 'Courses',
    'forum': 'Forums',
    'thread': 'Threads',
  };

  if (pathnames.length === 0) return null;

  return (
    <nav className="breadcrumbs animate-in">
      <Link to="/">Dashboard</Link>
      {pathnames.map((value, index) => {
        const last = index === pathnames.length - 1;
        const to = `/${pathnames.slice(0, index + 1).join('/')}`;
        const name = segmentMap[value] || value;

        // Don't show numeric IDs in breadcrumbs if possible, or handle them
        if (!isNaN(value)) return null;

        return (
          <React.Fragment key={to}>
            <ChevronRight size={14} />
            {last ? (
              <span className="current">{name}</span>
            ) : (
              <Link to={to}>{name}</Link>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
};

export default Breadcrumbs;
