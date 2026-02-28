/**
 * Страница услуг. Клиент — только просмотр. Admin — добавление/редактирование.
 */
import { useEffect, useState } from 'react';
import { servicesApi } from '../../api/servicesApi';
import { useAuthStore } from '../../store/authStore';

export default function ServicesPage() {
  const [services, setServices] = useState<any[]>([]);
  const user = useAuthStore((s) => s.user);
  const isAdmin = user?.role === 'admin';

  useEffect(() => {
    servicesApi.list().then((r) => setServices(r.data));
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Услуги</h1>
      <table className="w-full border-collapse">
        <thead>
          <tr className="bg-primary-light">
            <th className="p-2 text-left">Название</th>
            <th className="p-2 text-left">Цена</th>
          </tr>
        </thead>
        <tbody>
          {services.map((s) => (
            <tr key={s.id} className="border-b">
              <td className="p-2">{s.name}</td>
              <td className="p-2">{s.price} ₽</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
