import React from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import { Layout } from './components/Layout';
import { Login } from './pages/Login';
import { Locations } from './pages/Locations';
import { Workers } from './pages/Workers';
import { Schedules } from './pages/Schedules';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading…</div>;
 if (!user) {
  return <Navigate to="/login" replace />;
}
  return <>{children}</>;
}

export default function App() {
  return (
  <Routes>
  <Route path="/login" element={<Login />} />
  <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
    <Route index element={<Navigate to="/locations" replace />} />
    <Route path="locations" element={<Locations />} />
    <Route path="workers" element={<Workers />} />
    <Route path="schedules" element={<Schedules />} />
  </Route>
  <Route path="*" element={<Navigate to="/login" replace />} />
</Routes>
  );
}
