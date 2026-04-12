import { useState, useEffect, useCallback } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import { LayoutDashboard, LogOut, PlusCircle } from 'lucide-react';
import './Dashboard.css';

const API_URL = 'https://resume-coach-541990120066.europe-west1.run.app/api';

export default function SidebarLayout({ user, onLogout }) {
  const [history, setHistory] = useState([]);
  const navigate = useNavigate();
  const location = useLocation();

  const fetchHistory = useCallback(async () => {
    try {
      const res = await axios.get(`${API_URL}/user/${user.id}/history/`);
      setHistory(res.data.history || []);
    } catch(e) { }
  }, [user.id]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory, location.pathname]); // Refresh history intelligently on navigation

  return (
    <div className="layout-row">
      <aside className="sidebar">
        <div className="sidebar-header">
          <div style={{display: 'flex', alignItems: 'center', gap: '0.8rem'}}>
            <LayoutDashboard className="icon-blue" />
            <div>
              <h2>Your History</h2>
              <p>Welcome, {user?.name?.split(' ')[0] || "User"}!</p>
            </div>
          </div>
          <button onClick={onLogout} className="btn-icon" title="Log Out"><LogOut size={18} /></button>
        </div>
        
        <button className="btn-outline full-width" style={{marginBottom: '1rem', borderColor: 'var(--primary)', color: 'var(--primary)'}} onClick={() => navigate('/main')}>
          <PlusCircle size={16} style={{display: 'inline', marginRight: '6px', verticalAlign: 'text-bottom'}} /> 
          New Analysis
        </button>

        <div className="history-list">
          {history.length === 0 ? <p className="empty-text">No scans yet.</p> : history.map(h => (
            <div 
              key={h.id} 
              className={`history-card ${location.pathname.includes(`/history/${h.id}`) ? 'active-card' : ''}`} 
              onClick={() => navigate(`/history/${h.id}`)}
            >
              <div className="clamp-text">{h.job}</div>
              <div className="flex-between" style={{marginTop: '0.5rem'}}>
                <span className="badge">Score: {h.ats_score}</span>
                <span className="date">{h.date}</span>
              </div>
            </div>
          ))}
        </div>
      </aside>

      <main className="main-content">
        <Outlet /> 
      </main>
    </div>
  );
}
