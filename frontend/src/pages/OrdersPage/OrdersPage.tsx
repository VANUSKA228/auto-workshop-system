/**
 * Страница заявок. ИСЛАМ: GET /orders/ (Master/Admin) или GET /orders/my (Client).
 * Фильтры: status, search, date_from, date_to. Badge статусов по цветам.
 */
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ordersApi } from '../../api/ordersApi';
import { useAuthStore } from '../../store/authStore';

const STATUS_COLORS: Record<string, string> = {
  new: 'bg-gray-200 text-gray-700',
  in_progress: 'bg-blue-200 text-blue-800',
  in_repair: 'bg-amber-200 text-amber-800',
  done: 'bg-green-200 text-green-800',
};

export default function OrdersPage() {
  const [orders, setOrders] = useState<any[]>([]);
  const user = useAuthStore((s) => s.user);

  useEffect(() => {
    const fetch = async () => {
      const fn = user?.role === 'client' ? ordersApi.listMy : ordersApi.list;
      const res = await fn();
      setOrders(res.data);
    };
    fetch();
  }, [user?.role]);

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Заявки</h1>
        <Link
          to="/orders/new"
          className="px-4 py-2 bg-primary text-white rounded-lg"
        >
          Создать заявку
        </Link>
      </div>
      <table className="w-full border-collapse">
        <thead>
          <tr className="bg-primary-light">
            <th className="p-2 text-left">ID</th>
            <th className="p-2 text-left">Дата</th>
            <th className="p-2 text-left">Статус</th>
            <th className="p-2 text-left">Клиент</th>
            <th className="p-2 text-left">Автомобиль</th>
          </tr>
        </thead>
        <tbody>
          {orders.map((o) => (
            <tr key={o.id} className="border-b">
              <td className="p-2">{o.id}</td>
              <td className="p-2">{new Date(o.created_at).toLocaleDateString()}</td>
              <td className="p-2">
                <span
                  className={`px-2 py-1 rounded ${STATUS_COLORS[o.status] || 'bg-gray-200'}`}
                >
                  {o.status}
                </span>
              </td>
              <td className="p-2">
                {o.client
                  ? `${o.client.last_name} ${o.client.first_name}`
                  : '-'}
              </td>
              <td className="p-2">{`${o.car_brand} ${o.car_model} ${o.car_year}`}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
