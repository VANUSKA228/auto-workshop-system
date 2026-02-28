import { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { ordersApi } from '../../api/ordersApi';
import { servicesApi } from '../../api/servicesApi';
import { workersApi, Worker } from '../../api/workersApi';
import { useAuthStore } from '../../store/authStore';
import { useToast } from '../../components/Toast/Toast';

const STATUS_LABELS: Record<string, string> = { new:'Новая', in_progress:'В работе', in_repair:'В ремонте', done:'Готово' };
const STATUS_COLORS: Record<string, string> = {
  new:'bg-gray-100 text-gray-700', in_progress:'bg-blue-100 text-blue-800',
  in_repair:'bg-amber-100 text-amber-800', done:'bg-green-100 text-green-800',
};

interface Order {
  id:number; client_id:number; master_id:number|null; car_brand:string; car_model:string;
  car_year:number; description:string|null; status:string; created_at:string;
  client:{id:number;first_name:string;last_name:string}|null;
  master:{id:number;first_name:string;last_name:string}|null;
  order_services:{service_id:number;service:{id:number;name:string;price:number}|null}[];
}

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [selectedOrder, setSelectedOrder] = useState<Order|null>(null);
  const [showModal, setShowModal] = useState(false);
  const [showContactModal, setShowContactModal] = useState(false);
  const [services, setServices] = useState<any[]>([]);
  const [workers, setWorkers] = useState<Worker[]>([]);
  const [editData, setEditData] = useState<any>({});
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState<number|null>(null);
  const user = useAuthStore((s) => s.user);
  const { showToast, ToastContainer } = useToast();

  const fetchOrders = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string,string> = {};
      if (search) params.search = search;
      if (statusFilter) params.status = statusFilter;
      if (dateFrom) params.date_from = dateFrom;
      if (dateTo) params.date_to = dateTo;
      const res = user?.role === 'client' ? await ordersApi.listMy() : await ordersApi.list(params);
      setOrders(res.data);
    } catch { showToast('Не удалось загрузить заявки','error'); }
    finally { setLoading(false); }
  }, [search, statusFilter, dateFrom, dateTo, user?.role]);

  useEffect(() => { fetchOrders(); }, [fetchOrders]);

  const openProcess = (order: Order) => {
    setSelectedOrder(order);
    setEditData({
      description: order.description ?? '',
      service_ids: order.order_services.map((os) => os.service_id),
      worker_id: '',
    });
    setShowModal(true);
    servicesApi.list().then((r) => setServices(r.data)).catch(() => {});
    workersApi.list().then((r) => setWorkers(r.data)).catch(() => {});
  };

  const handleSave = async () => {
    if (!selectedOrder) return;
    setSaving(true);
    try {
      const payload: any = { description: editData.description || null, service_ids: editData.service_ids };
      if (editData.worker_id) payload.worker_id = Number(editData.worker_id);
      await ordersApi.update(selectedOrder.id, payload);
      showToast('Изменения сохранены', 'success');
      setShowModal(false);
      fetchOrders();
    } catch {
      showToast('Не удалось сохранить', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleDone = async () => {
    if (!selectedOrder) return;
    setSaving(true);
    try {
      await ordersApi.update(selectedOrder.id, { status:'done' });
      showToast(`Заявка #${selectedOrder.id} завершена!`,'success');
      setShowModal(false); setShowContactModal(true); fetchOrders();
    } catch { showToast('Ошибка','error'); }
    finally { setSaving(false); }
  };

  const handleDelete = async (order: Order) => {
    if (!window.confirm(`Удалить заявку #${order.id}?`)) return;
    setDeleting(order.id);
    try {
      await ordersApi.delete(order.id);
      showToast(`Заявка #${order.id} удалена`,'success'); fetchOrders();
    } catch (e:any) { showToast(e?.response?.data?.detail || 'Не удалось удалить','error'); }
    finally { setDeleting(null); }
  };

  const toggleService = (id:number) => setEditData((p:any) => ({
    ...p, service_ids: p.service_ids.includes(id) ? p.service_ids.filter((s:number)=>s!==id) : [...p.service_ids, id]
  }));

  const isMasterOrAdmin = user?.role === 'master' || user?.role === 'admin';

  return (
    <div className="max-w-7xl mx-auto">
      <ToastContainer />
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-primary-dark">Заявки</h1>
        <Link to="/orders/new" className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition font-medium">
          + Создать заявку
        </Link>
      </div>

      {isMasterOrAdmin && (
        <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4 flex flex-wrap gap-3 shadow-sm">
          <input type="text" placeholder="Поиск по клиенту или авто..." value={search} onChange={(e)=>setSearch(e.target.value)}
            className="border rounded-lg px-3 py-2 flex-1 min-w-44 focus:outline-none focus:ring-2 focus:ring-primary" />
          <select value={statusFilter} onChange={(e)=>setStatusFilter(e.target.value)}
            className="border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary">
            <option value="">Все статусы</option>
            {Object.entries(STATUS_LABELS).map(([k,v])=><option key={k} value={k}>{v}</option>)}
          </select>
          <input type="date" value={dateFrom} onChange={(e)=>setDateFrom(e.target.value)}
            className="border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary" />
          <input type="date" value={dateTo} onChange={(e)=>setDateTo(e.target.value)}
            className="border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary" />
          {(search||statusFilter||dateFrom||dateTo) && (
            <button onClick={()=>{setSearch('');setStatusFilter('');setDateFrom('');setDateTo('');}}
              className="px-3 py-2 text-gray-500 hover:text-danger border rounded-lg">✕ Сбросить</button>
          )}
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 overflow-x-auto shadow-sm">
        {loading ? (
          <div className="p-12 text-center text-gray-400">Загрузка...</div>
        ) : orders.length === 0 ? (
          <div className="p-12 text-center text-gray-400">
            <p className="text-4xl mb-3">📋</p><p>Заявок не найдено</p>
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="bg-primary-light border-b border-gray-200">
                {['ID','Дата','Статус','Клиент','Автомобиль','Услуги','Описание'].map(h=>(
                  <th key={h} className="p-3 text-left text-sm font-semibold text-primary-dark">{h}</th>
                ))}
                {isMasterOrAdmin && <th className="p-3 text-left text-sm font-semibold text-primary-dark">Действия</th>}
              </tr>
            </thead>
            <tbody>
              {orders.map((o,i) => (
                <tr key={o.id} className={`border-b hover:bg-blue-50/30 transition ${i%2===1?'bg-gray-50/40':''}`}>
                  <td className="p-3 text-sm font-mono text-gray-500">#{o.id}</td>
                  <td className="p-3 text-sm text-gray-600 whitespace-nowrap">{new Date(o.created_at).toLocaleDateString('ru-RU')}</td>
                  <td className="p-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[o.status]||'bg-gray-100'}`}>
                      {STATUS_LABELS[o.status]||o.status}
                    </span>
                  </td>
                  <td className="p-3 text-sm">{o.client ? `${o.client.last_name} ${o.client.first_name}` : '—'}</td>
                  <td className="p-3 text-sm whitespace-nowrap">{o.car_brand} {o.car_model} {o.car_year}</td>
                  <td className="p-3 text-sm text-gray-600 max-w-[150px]">
                    <span className="block truncate">{o.order_services.map(os=>os.service?.name).filter(Boolean).join(', ')||'—'}</span>
                  </td>
                  <td className="p-3 text-sm text-gray-500 max-w-[180px]">
                    <span className="block truncate">{o.description||'—'}</span>
                  </td>
                  {isMasterOrAdmin && (
                    <td className="p-3">
                      <div className="flex gap-1 flex-wrap">
                        {o.status !== 'done' && (
                          <button onClick={()=>openProcess(o)}
                            className="px-2 py-1 bg-primary text-white text-xs rounded hover:bg-primary-dark transition">
                            Обработать
                          </button>
                        )}
                        <button onClick={()=>{setSelectedOrder(o);setShowContactModal(true);}}
                          className="px-2 py-1 border border-primary text-primary text-xs rounded hover:bg-primary-light transition">
                          Связаться
                        </button>
                        {(o.status==='new'||o.status==='in_progress') && (
                          <button onClick={()=>handleDelete(o)} disabled={deleting===o.id}
                            className="px-2 py-1 border border-danger text-danger text-xs rounded hover:bg-red-50 transition disabled:opacity-50">
                            {deleting===o.id?'...':'Удалить'}
                          </button>
                        )}
                      </div>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Process Modal */}
      {showModal && selectedOrder && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div className="p-5 border-b flex justify-between items-start">
              <div>
                <h2 className="text-lg font-bold text-primary-dark">Заявка #{selectedOrder.id} — Обработка</h2>
                <p className="text-sm text-gray-500">{selectedOrder.client?.last_name} {selectedOrder.client?.first_name} · {selectedOrder.car_brand} {selectedOrder.car_model} {selectedOrder.car_year}</p>
              </div>
              <button onClick={()=>setShowModal(false)} className="text-gray-400 hover:text-gray-600 text-xl leading-none">✕</button>
            </div>
            <div className="p-5 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Исполнитель (работник)</label>
                <select
                  value={editData.worker_id || ''}
                  onChange={(e) => setEditData((p: any) => ({ ...p, worker_id: e.target.value }))}
                  className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="">— не назначен —</option>
                  {workers.map((w) => (
                    <option key={w.id} value={w.id}>
                      {w.last_name} {w.first_name}
                      {w.is_assigned ? ' (уже назначен)' : ''}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Услуги</label>
                <div className="border rounded-lg p-3 max-h-36 overflow-y-auto space-y-1">
                  {services.map((s)=>(
                    <label key={s.id} className="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-1 rounded">
                      <input type="checkbox" className="accent-primary" checked={editData.service_ids?.includes(s.id)} onChange={()=>toggleService(s.id)} />
                      <span className="text-sm flex-1">{s.name}</span>
                      {s.price && <span className="text-xs text-gray-400">{Number(s.price).toLocaleString('ru-RU')} ₽</span>}
                    </label>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Комментарий</label>
                <textarea value={editData.description} onChange={(e)=>setEditData((p:any)=>({...p,description:e.target.value}))}
                  rows={3} className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                  placeholder="Комментарий мастера..." />
              </div>
            </div>
            <div className="p-5 border-t flex gap-3">
              <button onClick={handleSave} disabled={saving}
                className="flex-1 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark disabled:opacity-50 font-medium transition">
                {saving?'Сохранение...':'Сохранить'}
              </button>
              {selectedOrder.status !== 'done' && (
                <button onClick={handleDone} disabled={saving}
                  className="flex-1 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 font-medium transition">
                  ✓ Готово
                </button>
              )}
              <button onClick={()=>setShowModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition">Отмена</button>
            </div>
          </div>
        </div>
      )}

      {/* Contact Modal */}
      {showContactModal && selectedOrder && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-sm">
            <div className="p-5 border-b flex justify-between items-center">
              <h2 className="text-lg font-bold text-primary-dark">📞 Контакты клиента</h2>
              <button onClick={()=>setShowContactModal(false)} className="text-gray-400 hover:text-gray-600 text-xl">✕</button>
            </div>
            <div className="p-5">
              <p className="font-semibold text-gray-800 mb-3">{selectedOrder.client?.last_name} {selectedOrder.client?.first_name}</p>
              <div className="bg-primary-light rounded-lg p-4 text-sm text-gray-600 space-y-1">
                <p>Авто: <span className="font-medium">{selectedOrder.car_brand} {selectedOrder.car_model} {selectedOrder.car_year}</span></p>
                <p className="text-gray-500 text-xs mt-2">Контактные данные клиента (телефон, email) доступны в разделе «Пользователи»</p>
              </div>
            </div>
            <div className="p-5 border-t">
              <button onClick={()=>setShowContactModal(false)}
                className="w-full py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition">Закрыть</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
