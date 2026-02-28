/**
 * Форма создания заявки. ИСЛАМ: валидация Yup, услуги из GET /services/.
 * После валидации — sessionStorage или store и переход на /payment.
 */
import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useNavigate } from 'react-router-dom';
import { servicesApi } from '../../api/servicesApi';

const schema = yup.object({
  car_brand: yup.string().required(),
  car_model: yup.string().required(),
  car_year: yup.number().min(1900).max(new Date().getFullYear()).required(),
  description: yup.string().max(1000),
  service_ids: yup.array().of(yup.number()).min(1, 'Выберите хотя бы одну услугу'),
});

type FormData = yup.InferType<typeof schema>;

export default function CreateOrderPage() {
  const [services, setServices] = useState<any[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    servicesApi.list().then((r) => setServices(r.data));
  }, []);

  const { register, handleSubmit, formState: { errors }, setValue, watch } = useForm<FormData>({
    resolver: yupResolver(schema),
    defaultValues: { service_ids: [] },
  });

  const selectedIds = watch('service_ids') || [];
  const total = services
    .filter((s) => selectedIds.includes(s.id))
    .reduce((sum, s) => sum + (s.price || 0), 0);

  const onSubmit = (data: FormData) => {
    sessionStorage.setItem(
      'orderDraft',
      JSON.stringify({ ...data, total, services: services.filter((s) => data.service_ids?.includes(s.id)) })
    );
    navigate('/payment');
  };

  return (
    <div className="max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Новая заявка</h1>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label>Марка</label>
          <input {...register('car_brand')} className="w-full border p-2 rounded" />
          {errors.car_brand && <p className="text-danger text-sm">{errors.car_brand.message}</p>}
        </div>
        <div>
          <label>Модель</label>
          <input {...register('car_model')} className="w-full border p-2 rounded" />
          {errors.car_model && <p className="text-danger text-sm">{errors.car_model.message}</p>}
        </div>
        <div>
          <label>Год</label>
          <input type="number" {...register('car_year', { valueAsNumber: true })} className="w-full border p-2 rounded" />
          {errors.car_year && <p className="text-danger text-sm">{errors.car_year.message}</p>}
        </div>
        <div>
          <label>Описание</label>
          <textarea {...register('description')} className="w-full border p-2 rounded" rows={3} />
        </div>
        <div>
          <label>Услуги</label>
          {services.map((s) => (
            <label key={s.id} className="block">
              <input
                type="checkbox"
                value={s.id}
                checked={selectedIds.includes(s.id)}
                onChange={(e) => {
                  const v = Number(e.target.value);
                  setValue(
                    'service_ids',
                    e.target.checked
                      ? [...selectedIds, v]
                      : selectedIds.filter((id) => id !== v)
                  );
                }}
              />
              {s.name} — {s.price} ₽
            </label>
          ))}
          {errors.service_ids && <p className="text-danger text-sm">{errors.service_ids.message}</p>}
        </div>
        <div className="flex gap-2">
          <button type="submit" className="px-4 py-2 bg-primary text-white rounded-lg">
            Далее →
          </button>
          <button
            type="button"
            onClick={() => navigate('/orders')}
            className="px-4 py-2 border rounded-lg"
          >
            Отмена
          </button>
        </div>
      </form>
    </div>
  );
}
