import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';
import { LogOut, LayoutDashboard, BrainCircuit, UploadCloud, Zap, Send } from 'lucide-react';
import './Dashboard.css';

const API_URL = 'https://resume-coach-541990120066.europe-west1.run.app/api';

export default function Dashboard({ user, onLogout }) {
  const [history, setHistory] = useState([]);
  const [jobDesc, setJobDesc] = useState('');
  const [file, setFile] = useState(null);
  
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [chatLoading, setChatLoading] = useState(false);

  const fetchHistory = useCallback(async () => {
    try {
      const res = await axios.get(`${API_URL}/user/${user.id}/history/`);
      setHistory(res.data.history || []);
    } catch(e) { }
  }, [user.id]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const onDrop = useCallback(acceptedFiles => {
    setFile(acceptedFiles[0]);
  }, []);
  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop, accept: {'application/pdf': ['.pdf']}, maxFiles: 1 });

  const handleAnalyze = async () => {
    if (!file || !jobDesc) {
      alert("Please provide both a PDF resume and a Job Description.");
      return;
    }
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('job_description', jobDesc);
    formData.append('user_id', user.id);

    try {
      const res = await axios.post(`${API_URL}/analyze/`, formData);
      setResults(res.data.data);
      setChatHistory([]); // Clear chat for new analysis
      fetchHistory(); // Refresh sidebar natively
    } catch(err) {
      alert("Analysis failed.");
    } finally {
      setLoading(false);
    }
  };

  const loadHistoryItem = async (id) => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_URL}/history/${id}`);
      setResults(res.data);
      setJobDesc(res.data.job_description);
      setFile(null); // File is archived on backend
      setChatHistory(res.data.chat_history || []);
    } catch(err) {
      alert("Failed to load archived record.");
    } finally {
      setLoading(false);
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
        context: results ? {
          job_desc: results.job_description || jobDesc,
          ats_score: results.ats_score,
          ats_match_level: results.ats_match_level,
          gap_analysis: results.gap_analysis,
          resume_text: results.resume_text
        } : {}
      });
      setChatHistory([...newHistory, { role: 'model', content: res.data.response }]);
    } catch(err) {
      setChatHistory([...newHistory, { role: 'model', content: 'Connection Error.' }]);
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <div className="layout-row">
      <aside className="sidebar">
        <div className="sidebar-header">
          <div style={{display: 'flex', alignItems: 'center', gap: '0.8rem'}}>
            <LayoutDashboard className="icon-blue" />
            <div>
              <h2>Your History</h2>
              <p>Welcome back, {user.name.split(' ')[0]}!</p>
            </div>
          </div>
          <button onClick={onLogout} className="btn-icon" title="Log Out"><LogOut size={18} /></button>
        </div>
        
        <div className="history-list">
          {history.length === 0 ? <p className="empty-text">No scans yet.</p> : history.map(h => (
            <div key={h.id} className="history-card" onClick={() => loadHistoryItem(h.id)}>
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
        <div className="content-container">
          <div className="page-header">
            <h1>ATS Match Analyzer</h1>
            <p>Upload your resume and paste the description to evaluate your compatibility.</p>
          </div>

          <div className="panel drop-panel">
            <div className="split-grid">
              <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
                <input {...getInputProps()} />
                <UploadCloud size={40} className="icon-blue" />
                <p>{file ? file.name : "Drag and drop your PDF here"}</p>
                <button className="btn-outline">Select PDF File</button>
              </div>
              <textarea 
                placeholder="Paste the target Job Description here..." 
                value={jobDesc} 
                onChange={e => setJobDesc(e.target.value)}
                className="base-textarea"
              ></textarea>
            </div>
            <button onClick={handleAnalyze} className="btn-primary full-width" disabled={loading} style={{marginTop: '1.5rem', height: '3rem', fontSize: '1.05rem'}}>
              {loading ? "Evaluating..." : "Evaluate Match against ATS"}
            </button>
          </div>

          {results && (
            <div className="panel results-panel">
              <div style={{display: 'flex', alignItems: 'center', gap: '1rem'}}>
                <Zap size={32} className="icon-blue" />
                <h2>Score: {results.ats_score}/100 - {results.ats_match_level}</h2>
              </div>
              <div className="gaps-container">
                <h4>Gaps Identified:</h4>
                <p className="highlight-text">{results.gap_analysis?.missing_keywords?.length > 0 ? results.gap_analysis.missing_keywords.join(", ") : "None"}</p>
                <p className="muted-text text-sm">{results.gap_analysis?.suggestions}</p>
              </div>
            </div>
          )}

          <div className="panel chat-panel">
            <div className="chat-header">
              <BrainCircuit className="icon-blue" />
              <h3>Resume Coach Chatbot</h3>
            </div>
            
            <div className="chat-window">
              {chatHistory.length === 0 ? <p className="empty-text">Start your interview prep here!</p> : chatHistory.map((msg, i) => (
                <div key={i} className={`chat-bubble ${msg.role === 'user' ? 'user' : 'ai'}`}>
                  {msg.content}
                </div>
              ))}
              {chatLoading && <div className="chat-bubble ai">Thinking...</div>}
            </div>

            <form onSubmit={sendChat} className="chat-input-area">
              <input 
                type="text" 
                placeholder="Ask for precise resume feedback..." 
                value={chatMessage} 
                onChange={e => setChatMessage(e.target.value)}
              />
              <button type="submit" disabled={chatLoading}><Send size={18} /> Send</button>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
}
