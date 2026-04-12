import { useState } from 'react';
import axios from 'axios';
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import { BrainCircuit, Mail, Lock, User } from 'lucide-react';
import { jwtDecode } from 'jwt-decode';

const API_URL = 'https://resume-coach-541990120066.europe-west1.run.app/api';
const GOOGLE_CLIENT_ID = "541990120066-u0ifhuki32pdpddv5dsklh3tqvq96qta.apps.googleusercontent.com";

export default function Login({ onLogin }) {
  const [isRegistering, setIsRegistering] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleManualAuth = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      const endpoint = isRegistering ? 'register/' : 'login/';
      const payload = isRegistering ? { email, name, password } : { email, password, is_oauth: false };
      
      const res = await axios.post(`${API_URL}/${endpoint}`, payload);
      onLogin(res.data.user);
    } catch(err) {
      setError(err.response?.data?.detail || "Authentication complete failure");
    } finally {
      setLoading(false);
    }
  };

  const handGoogleSuccess = async (response) => {
    try {
      const decoded = jwtDecode(response.credential);
      const res = await axios.post(`${API_URL}/google-login/`, {
        credential: response.credential
      });
      onLogin(res.data.user);
    } catch(err) {
      setError("Google Auth Failure: Check server.");
    }
  };

  return (
    <div className="layout-row" style={{justifyContent: 'center', alignItems: 'center', height: '100vh', width: '100vw'}}>
      <div className="content-container slide-up-anim" style={{maxWidth: '440px', padding: '0', width: '100%'}}>
        
        <div style={{textAlign: 'center', marginBottom: '2rem'}}>
          <BrainCircuit size={48} className="icon-blue pulse-anim" style={{margin: '0 auto 1rem auto'}} />
          <h1 style={{fontSize: '2.2rem', fontWeight: 800, color: 'var(--text-dark)', marginBottom: '0.5rem'}}>Resume Coach</h1>
          <p style={{color: 'var(--text-muted)'}}>AI Interview Analysis for Top 1% Applicants.</p>
        </div>

        <div className="panel glass-panel glow-border" style={{padding: '2.5rem', boxShadow: '0 25px 50px -12px rgba(0,0,0,0.1)'}}>
          
          {error && <div style={{color: '#ef4444', fontSize: '0.9rem', marginBottom: '1rem', padding: '0.75rem', background: '#fef2f2', border: '1px solid #fca5a5', borderRadius: '8px', textAlign: 'center', fontWeight: '500'}}>{error}</div>}

          <form onSubmit={handleManualAuth} style={{display: 'flex', flexDirection: 'column', gap: '1.25rem'}}>
            
            {isRegistering && (
              <div style={{position: 'relative'}}>
                <User size={18} style={{position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)'}} />
                <input type="text" placeholder="Full Name" value={name} onChange={e => setName(e.target.value)} required className="glass-input" style={{width: '100%', padding: '0.75rem 1rem 0.75rem 2.8rem'}} />
              </div>
            )}
            
            <div style={{position: 'relative'}}>
              <Mail size={18} style={{position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)'}} />
              <input type="email" placeholder="Email Address" value={email} onChange={e => setEmail(e.target.value)} required className="glass-input" style={{width: '100%', padding: '0.75rem 1rem 0.75rem 2.8rem'}} />
            </div>

            <div style={{position: 'relative'}}>
              <Lock size={18} style={{position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)'}} />
              <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} required className="glass-input" style={{width: '100%', padding: '0.75rem 1rem 0.75rem 2.8rem'}} />
            </div>

            <button type="submit" className="btn-primary hover-lift" disabled={loading} style={{height: '3rem', marginTop: '0.5rem'}}>
              {loading ? 'Processing...' : (isRegistering ? 'Establish Account' : 'Secure Login')}
            </button>
            <p style={{textAlign: 'center', marginTop: '0.5rem', cursor: 'pointer', color: 'var(--primary)', fontWeight: 600, fontSize: '0.9rem'}} onClick={() => setIsRegistering(!isRegistering)}>
              {isRegistering ? "Already hold an account? Sign In." : "First time? Register here."}
            </p>
          </form>

          <div style={{display: 'flex', alignItems: 'center', margin: '2rem 0', color: '#94A3B8'}}>
            <div style={{flex: 1, height: '1px', background: 'var(--border-light)'}}></div>
            <span style={{padding: '0 1rem', fontSize: '0.85rem', fontWeight: 600, letterSpacing: '0.05em'}}>OR CONTINUE WITH</span>
            <div style={{flex: 1, height: '1px', background: 'var(--border-light)'}}></div>
          </div>

          <div style={{display: 'flex', justifyContent: 'center'}}>
            <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
              <GoogleLogin onSuccess={handGoogleSuccess} onError={() => setError("Google Auth Failed")} useOneTap theme="outline" shape="pill" />
            </GoogleOAuthProvider>
          </div>
        </div>

      </div>
    </div>
  );
}
