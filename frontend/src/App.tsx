import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './contexts/AuthContext';
import { SocketProvider } from './contexts/SocketContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import NodeDetail from './pages/NodeDetail';
import Terminal from './pages/Terminal';
import Settings from './pages/Settings';

function App() {
  return (
    <AuthProvider>
      <SocketProvider>
        <Router>
          <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/" element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } />
              <Route path="/node/:nodeId" element={
                <ProtectedRoute>
                  <NodeDetail />
                </ProtectedRoute>
              } />
              <Route path="/terminal/:nodeId" element={
                <ProtectedRoute>
                  <Terminal />
                </ProtectedRoute>
              } />
              <Route path="/settings" element={
                <ProtectedRoute>
                  <Settings />
                </ProtectedRoute>
              } />
            </Routes>
            <Toaster 
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#1f2937',
                  color: '#f3f4f6',
                  border: '1px solid #374151',
                },
                success: {
                  style: {
                    background: '#065f46',
                    color: '#d1fae5',
                    border: '1px solid #10b981',
                  },
                },
                error: {
                  style: {
                    background: '#7f1d1d',
                    color: '#fee2e2',
                    border: '1px solid #ef4444',
                  },
                },
              }}
            />
          </div>
        </Router>
      </SocketProvider>
    </AuthProvider>
  );
}

export default App;
