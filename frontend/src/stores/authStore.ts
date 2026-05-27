import { create } from 'zustand';

interface AuthState {
  token: string | null;
  isAdmin: boolean;
  setToken: (token: string | null) => void;
  setIsAdmin: (isAdmin: boolean) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  isAdmin: false,
  setToken: (token) => set({ token }),
  setIsAdmin: (isAdmin) => set({ isAdmin }),
}));
