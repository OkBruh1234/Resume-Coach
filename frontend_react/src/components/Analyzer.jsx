import { useState, useCallback } from 'react';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, Zap, BrainCircuit, Send } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const API_URL = 'https://resume-coach-541990120066.europe-west1.run.app/api';

export default function Analyzer({ user }) {
  const [jobDesc, setJobDesc] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onDrop = useCallback(acceptedFiles => {
    setFile(acceptedFiles[0]);
  }, []);
  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop, accept: {'application/pdf': ['.pdf']}, maxFiles: 1 });

  const handleAnalyze = async () => {
    if (!file || !jobDesc) return alert("Provide a PDF and Job Description.");
    setLoading(true);
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('job_description', jobDesc);
    formData.append('user_id', user.id);

    try {
      const res = await axios.post(`${API_URL}/analyze/`, formData);
      navigate(`/history/${res.data.data.id}`); // Auto-redirect to the detailed history view once computed successfully!
    } catch(err) {
      alert("Analysis failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="content-container slide-up-anim">
      <div className="page-header">
        <h1>ATS Match Analyzer</h1>
        <p>Drop your resume and paste the description below to evaluate compatibility.</p>
      </div>

      <div className="panel drop-panel glass-panel">
        <div className="split-grid">
          <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
            <input {...getInputProps()} />
            <UploadCloud size={40} className="icon-blue pulse-anim" />
            <p>{file ? file.name : "Drag your PDF here"}</p>
            <button className="btn-outline">Select PDF File</button>
          </div>
          <textarea 
            placeholder="Paste the target Job Description exactly here..." 
            value={jobDesc} 
            onChange={e => setJobDesc(e.target.value)}
            className="base-textarea glass-input"
          ></textarea>
        </div>
        <button onClick={handleAnalyze} className="btn-primary full-width hover-lift" disabled={loading} style={{marginTop: '1.5rem', height: '3rem', fontSize: '1.05rem'}}>
          {loading ? "Evaluating..." : "Evaluate Match against ATS"}
        </button>
      </div>
    </div>
  );
}
