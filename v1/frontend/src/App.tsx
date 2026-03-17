import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import LoginPage from './pages/LoginPage/LoginPage';
import ClientRegisterPage from './pages/ClientRegisterPage/ClientRegisterPage';
import Layout from './components/Layout/Layout';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((s) => s.token);
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

function OrdersPlaceholder() {
  return (
    <div className="p-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-primary-dark mb-4">📋 Мои заявки</h2>
      </div>
    </div>
  );
}

function ServicesPlaceholder() {
  return (
    <div className="p-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-primary-dark mb-4">🔧 Услуги</h2>
      </div>
    </div>
  );
}

function WorkersPlaceholder() {
  return (
    <div className="p-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-primary-dark mb-4">👷 Работники</h2>
      </div>
    </div>
  );
}

function UsersPlaceholder() {
  return (
    <div className="p-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-primary-dark mb-4">👥 Пользователи</h2>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<ClientRegisterPage />} />
      <Route
        path="/app"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="orders" element={<OrdersPlaceholder />} />
        <Route path="services" element={<ServicesPlaceholder />} />
        <Route path="workers" element={<WorkersPlaceholder />} />
        <Route path="users" element={<UsersPlaceholder />} />
      </Route>
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
