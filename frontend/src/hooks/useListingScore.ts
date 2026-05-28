import { useQuery } from "@tanstack/react-query";
import api from "../lib/api";

export function useListingScore(id: string | null) {
  return useQuery({
    queryKey: ["listing", id, "score"],
    queryFn: async () => {
      const { data } = await api.get(`/listings/${id}/score`);
      return data;
    },
    enabled: !!id,
    staleTime: 60_000,
  });
}

export function useListingPriceEstimate(id: string | null) {
  return useQuery({
    queryKey: ["listing", id, "price"],
    queryFn: async () => {
      const { data } = await api.get(`/listings/${id}/price-estimate`);
      return data;
    },
    enabled: !!id,
    staleTime: 300_000,
  });
}

export function useListingPOIs(id: string | null) {
  return useQuery({
    queryKey: ["listing", id, "pois"],
    queryFn: async () => {
      const { data } = await api.get(`/listings/${id}/pois`);
      return data;
    },
    enabled: !!id,
    staleTime: 3_600_000,
  });
}

export function useListingGrowthSignals(id: string | null) {
  return useQuery({
    queryKey: ["listing", id, "growth"],
    queryFn: async () => {
      const { data } = await api.get(`/listings/${id}/growth-signals`);
      return data;
    },
    enabled: !!id,
    staleTime: 3_600_000,
  });
}
