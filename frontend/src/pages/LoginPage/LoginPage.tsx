/**
 * Страница входа. ИСЛАМ: форма React Hook Form + Yup,
 * POST /auth/login → token и user → localStorage + store → redirect /orders.
 */
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../../api/authApi';
import { useAuthStore } from '../../store/authStore';

const schema = yup.object({
  email: yup.string().email('Неверный формат email').required('Обязательное поле'),
  password: yup.string().min(6, 'Минимум 6 символов').required('Обязательное поле'),
});

type FormData = yup.InferType<typeof schema>;

export default function LoginPage() {
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({ resolver: yupResolver(schema) });

  const onSubmit = async (data: FormData) => {
    setError('');
    try {
      const res = await authApi.login(data);
      const { token, user } = res.data;
      setAuth(token, { id: user.id, name: user.name, role: user.role });
      navigate('/orders');
    } catch (e: unknown) {
      setError('Неверный email или пароль');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-primary-light">
      <div className="w-full max-w-md p-6 bg-white rounded-lg shadow">
        <h1 className="text-2xl font-bold text-center mb-6">Автосервис</h1>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <input
              type="email"
              placeholder="example@mail.ru"
              {...register('email')}
              className="w-full px-4 py-2 border rounded-lg"
            />
            {errors.email && (
              <p className="text-danger text-sm mt-1">{errors.email.message}</p>
            )}
          </div>
          <div>
            <input
              type="password"
              placeholder="••••••••"
              {...register('password')}
              className="w-full px-4 py-2 border rounded-lg"
            />
            {errors.password && (
              <p className="text-danger text-sm mt-1">{errors.password.message}</p>
            )}
          </div>
          {error && (
            <div className="p-2 bg-red-100 text-danger rounded"> {error}</div>
          )}
          <button
            type="submit"
            className="w-full py-2 bg-primary text-white rounded-lg hover:bg-primary-dark"
          >
            Войти
          </button>
        </form>
      </div>
    </div>
  );
}
