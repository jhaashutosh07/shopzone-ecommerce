import { create } from 'zustand';
import { api } from './api';

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  total_orders: number;
  total_returns: number;
  return_rate: number;
}

interface CartItem {
  id: string;
  product_id: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  product_name: string;
  product_image: string;
  product_in_stock: boolean;
  product_stock_quantity: number;
}

interface Cart {
  id: string;
  items: CartItem[];
  total_items: number;
  subtotal: number;
  tax: number;
  total: number;
}

interface AppState {
  user: User | null;
  cart: Cart | null;
  isLoading: boolean;
  isAuthenticated: boolean;

  // Auth actions
  login: (email: string, password: string) => Promise<void>;
  register: (data: { email: string; password: string; full_name: string }) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;

  // Cart actions
  fetchCart: () => Promise<void>;
  addToCart: (productId: string, quantity?: number) => Promise<void>;
  updateCartItem: (itemId: string, quantity: number) => Promise<void>;
  removeFromCart: (itemId: string) => Promise<void>;
  clearCart: () => Promise<void>;
}

export const useStore = create<AppState>((set, get) => ({
  user: null,
  cart: null,
  isLoading: true,
  isAuthenticated: false,

  login: async (email: string, password: string) => {
    const response = await api.login(email, password);
    api.setToken(response.access_token);
    set({ user: response.user, isAuthenticated: true });
    await get().fetchCart();
  },

  register: async (data) => {
    const response = await api.register(data);
    api.setToken(response.access_token);
    set({ user: response.user, isAuthenticated: true });
    await get().fetchCart();
  },

  logout: () => {
    api.setToken(null);
    set({ user: null, cart: null, isAuthenticated: false });
  },

  checkAuth: async () => {
    const token = api.getToken();
    if (!token) {
      set({ isLoading: false, isAuthenticated: false });
      return;
    }

    try {
      const user = await api.getMe();
      set({ user, isAuthenticated: true, isLoading: false });
      await get().fetchCart();
    } catch {
      api.setToken(null);
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  fetchCart: async () => {
    if (!get().isAuthenticated) return;
    try {
      const cart = await api.getCart();
      set({ cart });
    } catch (error) {
      console.error('Failed to fetch cart:', error);
    }
  },

  addToCart: async (productId: string, quantity = 1) => {
    const cart = await api.addToCart(productId, quantity);
    set({ cart });
  },

  updateCartItem: async (itemId: string, quantity: number) => {
    const cart = await api.updateCartItem(itemId, quantity);
    set({ cart });
  },

  removeFromCart: async (itemId: string) => {
    const cart = await api.removeCartItem(itemId);
    set({ cart });
  },

  clearCart: async () => {
    await api.clearCart();
    set({ cart: null });
    await get().fetchCart();
  },
}));
