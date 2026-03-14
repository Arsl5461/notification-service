import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ErrorBoundary } from './components/ErrorBoundary';
import App from './App';
import './index.css';

// Standalone (separate service): basename ''. Under API at /admin: basename '/admin'
const basename = import.meta.env.VITE_API_BASE ? '' : (import.meta.env.BASE_URL || '/admin').replace(/\/$/, '') || '/admin';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <BrowserRouter
        basename={basename}
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true,
        }}
      >
        <AuthProvider>
          <App />
        </AuthProvider>
      </BrowserRouter>
    </ErrorBoundary>
  </React.StrictMode>
);
