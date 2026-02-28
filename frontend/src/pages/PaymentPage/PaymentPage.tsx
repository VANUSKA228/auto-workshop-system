/**
 * Страница оплаты — ЗАГЛУШКА. Данные карты НЕ сохраняются.
 * ИСЛАМ: поля карты — маска (react-input-mask). Кнопка «Оплатить»:
 * 1. POST /orders/ — создаёт заявку
 * 2. POST /payments/stub { order_id, amount }
 * 3. redirect /orders + toast «Заявка #N успешно создана»
 */
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ordersApi } from '../../api/ordersApi';
import { paymentsApi } from '../../api/paymentsApi';

export default function PaymentPage() {
  const [draft, setDraft] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const raw = sessionStorage.getItem('orderDraft');
    if (!raw) {
      navigate('/orders/new');
      return;
    }
    setDraft(JSON.parse(raw));
  }, [navigate]);

  const handlePay = async () => {
    if (!draft) return;
    setLoading(true);
    try {
      const orderRes = await ordersApi.create({
        car_brand: draft.car_brand,
        car_model: draft.car_model,
        car_year: draft.car_year,
        description: draft.description,
        service_ids: draft.service_ids,
      });
      const orderId = orderRes.data.id;
      await paymentsApi.stub({ order_id: orderId, amount: draft.total });
      sessionStorage.removeItem('orderDraft');
      navigate('/orders');
      alert(`Заявка #${orderId} успешно создана`);
    } catch {
      alert('Что-то пошло не так, попробуйте ещё раз');
    } finally {
      setLoading(false);
    }
  };

  if (!draft) return <div>Загрузка...</div>;

  return (
    <div className="max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Оплата услуг</h1>
      <div className="bg-primary-light p-4 rounded-lg mb-4">
        <p>Автомобиль: {draft.car_brand} {draft.car_model} {draft.car_year}</p>
        <p>Итого: {draft.total} ₽</p>
      </div>
      <p className="text-sm text-gray-500 mb-4">
        Тестовый режим. Реальное списание не производится.
      </p>
      <button
        onClick={handlePay}
        disabled={loading}
        className="w-full py-2 bg-green-600 text-white rounded-lg disabled:opacity-50"
      >
        {loading ? 'Обработка...' : `Оплатить ${draft.total} руб.`}
      </button>
      <button
        onClick={() => navigate('/orders/new')}
        className="mt-2 text-primary underline"
      >
        ← Назад
      </button>
    </div>
  );
}
