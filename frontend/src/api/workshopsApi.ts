import api from './axiosInstance';

export interface Workshop {
  id: number;
  name: string;
  city: string;
}

export const workshopsApi = {
  list: () => api.get<Workshop[]>('/workshops/'),
};

