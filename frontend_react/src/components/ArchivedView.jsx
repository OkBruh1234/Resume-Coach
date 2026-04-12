import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Zap, BrainCircuit, Send, ArrowLeft, Lock } from 'lucide-react';

const API_URL = 'https://resume-coach-541990120066.europe-west1.run.app/api';

const safeRender = (val) => {
  if (!val) return "None";
  if (typeof val === 'string' || typeof val === 'number') return val;
  if (Array.isArray(val)) return val.join(", ");
  return JSON.stringify(val);
};

export default function ArchivedView({ user }) {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [chatLoading, setChatLoading] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const res = await axios.get(`${API_URL}/history/${id}`);
        setResults(res.data);
        setChatHistory(res.data.chat_history || []);
      } catch (err) {
        navigate('/main');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [id, navigate]);

  const handleUpgrade = async () => {
    try {
      await axios.post(`${API_URL}/upgrade-pro/`, { user_id: String(user.id) });
      const newUserData = { ...user, is_pro: true };
      localStorage.setItem('userData', JSON.stringify(newUserData));
      window.location.reload(); 
    } catch(err) {
      alert("Payment test failed.");
    }
  };

  const sendChat = async (e) => {
    e.preventDefault();
    if (!chatMessage.trim()) return;

    const newHistory = [...chatHistory, { role: 'user', content: chatMessage }];
    setChatHistory(newHistory);
    setChatMessage('');
    setChatLoading(true);

    try {
      const res = await axios.post(`${API_URL}/chat/`, {
        message: chatMessage,
        history: chatHistory,
        user_id: String(user.id),
        analysis_id: results ? results.id : null,
        context: {
          job_desc: results.job_description,
          ats_score: results.ats_score,
          ats_match_level: results.ats_match_level,
          gap_analysis: results.gap_analysis,
          resume_text: results.resume_text
        }
      });
      setChatHistory([...newHistory, { role: 'model', content: res.data.response }]);
    } catch(err) {
      setChatHistory([...newHistory, { role: 'model', content: 'Connection Error.' }]);
    } finally {
      setChatLoading(false);
    }
  };

  if (loading || !results) return <div className="loading-state">Hydrating Record...</div>;

  return (
    <div className="content-container slide-up-anim">
      <div style={{display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem'}}>
        <button onClick={() => navigate('/main')} className="btn-icon" style={{color: 'var(--text-muted)'}}><ArrowLeft size={20}/></button>
        <span style={{color: 'var(--text-muted)', fontSize:'0.9rem', fontWeight: 600}}>ARCHIVE #{id}</span>
      </div>

      <div className="panel results-panel glass-panel glow-border">
        <div style={{display: 'flex', alignItems: 'center', gap: '1rem'}}>
          <Zap size={32} className="icon-blue pulse-anim" />
          <h2 style={{fontSize:'1.8rem', fontWeight: 800}}>Score: {results.ats_score}/100 - {results.ats_match_level}</h2>
        </div>
        <div className="gaps-container">
          <h4>Gaps Identified:</h4>
          <p className="highlight-text">
            {safeRender(results?.gap_analysis?.missing_keywords)}
          </p>
          <p className="muted-text">
            {safeRender(results?.gap_analysis?.suggestions)}
          </p>
        </div>
      </div>

      <div className="panel chat-panel glass-panel">
        <div className="chat-header">
          <BrainCircuit className="icon-blue" />
          <h3 style={{fontWeight: 700}}>Resume Coach AI</h3>
        </div>
        
        <div className="chat-window custom-scrollbar">
          {chatHistory.length === 0 ? <p className="empty-text" style={{marginTop:'auto', marginBottom:'auto'}}>Ask a question about this resume's gaps to begin.</p> : chatHistory.map((msg, i) => (
            <div key={i} className={`chat-bubble ${msg.role === 'user' ? 'user' : 'ai'} pop-in-anim`}>
              {msg.content}
            </div>
          ))}
          {chatLoading && <div className="chat-bubble ai pulse-anim">Thinking dynamically...</div>}
        </div>

        {(!user.is_pro && chatHistory.filter(m => m.role === 'user').length >= 3) ? (
          <div className="paywall-overlay pop-in-anim">
            <Lock size={20} className="icon-blue" />
            <p><strong>Free Limit Reached (3/3)</strong></p>
            <p className="text-sm muted-text mb-1">Upgrade to Premium for unlimited AI interview coaching and absolute priority execution.</p>
            <button onClick={handleUpgrade} className="btn-primary" style={{marginTop: '0.5rem'}}>
              Unlock Pro Now
            </button>
          </div>
        ) : (
          <form onSubmit={sendChat} className="chat-input-area">
            <input 
              type="text" 
              placeholder="Ask for precise resume feedback..." 
              value={chatMessage} 
              onChange={e => setChatMessage(e.target.value)}
              className="glass-input"
            />
            <button type="submit" disabled={chatLoading} className="hover-lift"><Send size={18} /> Send</button>
          </form>
        )}
      </div>
    </div>
  );
}
