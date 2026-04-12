import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { CreditCard, CheckCircle, ShieldCheck, ArrowLeft, Zap } from 'lucide-react';

const API_URL = 'https://resume-coach-541990120066.europe-west1.run.app/api';

export default function Checkout({ user, setUser }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handlePayment = async (e) => {
    e.preventDefault();
    setLoading(true);

    // Mock network validation delay (simulating Stripe processing)
    setTimeout(async () => {
      try {
        await axios.post(`${API_URL}/upgrade-pro/`, { user_id: String(user.id) });
        const newUserData = { ...user, is_pro: true };
        localStorage.setItem('userData', JSON.stringify(newUserData));
        setUser(newUserData);
        setSuccess(true);
        setTimeout(() => navigate('/main'), 2000);
      } catch (err) {
        alert(`Payment error: ${err.message}`);
        setLoading(false);
      }
    }, 1500);
  };

  if (success) {
    return (
      <div className="content-container slide-up-anim" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <CheckCircle size={80} style={{ color: '#2ecc71', marginBottom: '1rem' }} className="pop-in-anim" />
        <h2 style={{ fontSize: '2rem', fontWeight: 800 }}>Payment Successful!</h2>
        <p className="muted-text mt-1">You are now a Premium AI Member. Redirecting you to your dashboard...</p>
      </div>
    );
  }

  return (
    <div className="content-container slide-up-anim">
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
        <button onClick={() => navigate(-1)} className="btn-icon" style={{ color: 'var(--text-muted)' }}>
          <ArrowLeft size={20} />
        </button>
        <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem', fontWeight: 600 }}>SECURE SECURE CHECKOUT</span>
      </div>

      <div className="panel glass-panel glow-border" style={{ maxWidth: '500px', margin: '0 auto', padding: '2rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <Zap size={40} className="icon-blue pulse-anim" style={{ marginBottom: '1rem' }} />
          <h2 style={{ fontSize: '1.8rem', fontWeight: 800 }}>Premium ATS Suite</h2>
          <p className="muted-text mt-1">Unlimited GPT-4o Resume Coaching & PDF Generation.</p>
        </div>

        <form onSubmit={handlePayment} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="input-group">
            <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)' }}>Card Information</label>
            <div style={{ position: 'relative' }}>
              <CreditCard size={18} style={{ position: 'absolute', top: '50%', transform: 'translateY(-50%)', left: '12px', color: 'var(--text-muted)' }} />
              <input 
                type="text" 
                placeholder="0000 0000 0000 0000" 
                className="glass-input" 
                style={{ paddingLeft: '40px', width: '100%', marginBottom: '0.5rem' }}
                required 
              />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
              <input type="text" placeholder="MM/YY" className="glass-input" required />
              <input type="text" placeholder="CVC" className="glass-input" required />
            </div>
          </div>

          <div className="input-group">
            <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)' }}>Cardholder Name</label>
            <input type="text" placeholder="Full Name" className="glass-input" required />
          </div>

          <button 
            type="submit" 
            className="btn-primary hover-lift" 
            style={{ padding: '0.75rem', marginTop: '1rem', fontSize: '1.1rem', fontWeight: 700 }}
            disabled={loading}
          >
            {loading ? "Processing..." : "Pay $14.99"}
          </button>
        </form>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', marginTop: '1.5rem', color: 'var(--text-muted)' }}>
          <ShieldCheck size={16} />
          <span style={{ fontSize: '0.8rem' }}>Payments process securely via Mock Stripe API</span>
        </div>
      </div>
    </div>
  );
}
