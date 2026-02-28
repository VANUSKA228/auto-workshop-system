/**
 * Navbar — отображается на всех страницах после входа.
 * ИСЛАМ: role === 'admin' — показывать Users, Reports.
 * Master — только Reports (без Users).
 * Client — Заявки, Услуги.
 */
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

export default function Navbar() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-primary-dark text-white p-4 flex items-center justify-between">
      <div className="flex gap-4">
        <NavLink to="/orders" className="font-bold">
          Автосервис
        </NavLink>
        <NavLink to="/orders" className={({ isActive }) => (isActive ? 'underline' : '')}>
          Заявки
        </NavLink>
        <NavLink to="/services" className={({ isActive }) => (isActive ? 'underline' : '')}>
          Услуги
        </NavLink>
        {(user?.role === 'admin' || user?.role === 'master') && (
          <NavLink to="/reports" className={({ isActive }) => (isActive ? 'underline' : '')}>
            Отчёты
          </NavLink>
        )}
        {user?.role === 'admin' && (
          <NavLink to="/users" className={({ isActive }) => (isActive ? 'underline' : '')}>
            Пользователи
          </NavLink>
        )}
      </div>
      <div className="flex items-center gap-4">
        {user && (
          <>
            <span className="text-sm">
              {user.name} [{user.role}]
            </span>
            <button
              onClick={handleLogout}
              className="px-3 py-1 rounded border border-white hover:bg-white/10"
            >
              Выйти
            </button>
          </>
        )}
      </div>
    </nav>
  );
}
