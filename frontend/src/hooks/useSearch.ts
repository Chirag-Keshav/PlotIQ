import { useQuery } from '@tanstack/react-query';
import api from '../lib/api';

interface SearchParams {
  query?: string;
  filters?: Record<string, any>;
}

export function useSearch(params: SearchParams) {
  return useQuery({
    queryKey: ['search', params],
    queryFn: async () => {
      const { data } = await api.post('/search', params);
      return data;
    },
    // Don't refetch on window focus for map search
    refetchOnWindowFocus: false,
    staleTime: 60000,
  });
}
