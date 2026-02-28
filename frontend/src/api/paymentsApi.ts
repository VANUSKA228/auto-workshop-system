import api from './axiosInstance';

export const paymentsApi = {
  stub: (data: { order_id: number; amount: number }) =>
    api.post('/payments/stub', data),
};
