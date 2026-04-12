import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import SidebarLayout from './components/SidebarLayout';
import Analyzer from './components/Analyzer';
import ArchivedView from './components/ArchivedView';
import Checkout from './components/Checkout';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    try {
      const savedUser = localStorage.getItem('userData');
      if (savedUser && savedUser !== 'undefined') {
        setUser(JSON.parse(savedUser));
      }
    } catch(err) {
      localStorage.removeItem('userData');
    }
    setLoading(false);
  }, []);

  const handleLogin = (userData) => {
    localStorage.setItem('userData', JSON.stringify(userData));
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('userData');
    setUser(null);
  };

  if (loading) return null;

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={
          user ? <Navigate to="/main" /> : <Login onLogin={handleLogin} />
        } />
        
        {/* Protected Dashboard Routes wrapped centrally in Sidebar Layout */}
        <Route path="/" element={user ? <SidebarLayout user={user} onLogout={handleLogout} /> : <Navigate to="/login" />}>
          <Route index element={<Navigate to="/main" />} />
          <Route path="main" element={<Analyzer user={user} />} />
          <Route path="history/:id" element={<ArchivedView user={user} />} />
          <Route path="checkout" element={<Checkout user={user} setUser={setUser} />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
