import { useQuery } from '@tanstack/react-query';
import api from '../lib/api';

export function useListing(id: string | null) {
  return useQuery({
    queryKey: ['listing', id],
    queryFn: async () => {
      const { data } = await api.get(`/listings/${id}`);
      return data;
    },
    enabled: !!id,
    staleTime: 300000, // 5 minutes
  });
}
