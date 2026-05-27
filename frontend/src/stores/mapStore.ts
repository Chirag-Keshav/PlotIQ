import { create } from 'zustand';

interface MapState {
  bounds: { north: number; south: number; east: number; west: number } | null;
  center: { lat: number; lng: number };
  zoom: number;
  activeFilters: Record<string, any>;
  searchQuery: string;
  selectedListingId: string | null;
  comparisonTray: string[];
  setBounds: (bounds: MapState['bounds']) => void;
  setCenter: (center: MapState['center']) => void;
  setZoom: (zoom: number) => void;
  setFilters: (filters: Record<string, any>) => void;
  setSearchQuery: (query: string) => void;
  setSelectedListing: (id: string | null) => void;
  toggleComparison: (id: string) => void;
}

export const useMapStore = create<MapState>((set) => ({
  bounds: null,
  center: { lat: 17.3850, lng: 78.4867 }, // Hyderabad default
  zoom: 11,
  activeFilters: {},
  searchQuery: '',
  selectedListingId: null,
  comparisonTray: [],
  
  setBounds: (bounds) => set({ bounds }),
  setCenter: (center) => set({ center }),
  setZoom: (zoom) => set({ zoom }),
  setFilters: (filters) => set({ activeFilters: filters }),
  setSearchQuery: (query) => set({ searchQuery: query }),
  setSelectedListing: (id) => set({ selectedListingId: id }),
  toggleComparison: (id) => set((state) => {
    const isSelected = state.comparisonTray.includes(id);
    if (isSelected) {
      return { comparisonTray: state.comparisonTray.filter(item => item !== id) };
    }
    // Limit to 3 comparisons
    if (state.comparisonTray.length >= 3) {
      return state;
    }
    return { comparisonTray: [...state.comparisonTray, id] };
  })
}));
