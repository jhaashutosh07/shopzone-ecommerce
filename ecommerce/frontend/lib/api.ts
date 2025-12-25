const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1';

class ApiClient {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
    if (typeof window !== 'undefined') {
      if (token) {
        localStorage.setItem('token', token);
      } else {
        localStorage.removeItem('token');
      }
    }
  }

  getToken(): string | null {
    if (this.token) return this.token;
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('token');
    }
    return this.token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = this.getToken();
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
      throw new Error(error.detail || 'An error occurred');
    }

    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  // Auth
  async register(data: { email: string; password: string; full_name: string; role?: string }) {
    return this.request<{ access_token: string; user: any }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async login(email: string, password: string) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    return response.json();
  }

  async getMe() {
    return this.request<any>('/auth/me');
  }

  async getAddresses() {
    return this.request<any[]>('/auth/addresses');
  }

  async addAddress(data: any) {
    return this.request<any>('/auth/addresses', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Products
  async getProducts(params?: Record<string, any>) {
    const query = params ? '?' + new URLSearchParams(params).toString() : '';
    return this.request<any[]>(`/products${query}`);
  }

  async getFeaturedProducts() {
    return this.request<any[]>('/products/featured');
  }

  async getDeals() {
    return this.request<any[]>('/products/deals');
  }

  async getProduct(id: string) {
    return this.request<any>(`/products/${id}`);
  }

  async getProductsByCategory(category: string) {
    return this.request<any[]>(`/products/category/${category}`);
  }

  // Cart
  async getCart() {
    return this.request<any>('/cart');
  }

  async addToCart(productId: string, quantity: number = 1, size?: string, color?: string) {
    return this.request<any>('/cart/items', {
      method: 'POST',
      body: JSON.stringify({
        product_id: productId,
        quantity,
        selected_size: size,
        selected_color: color,
      }),
    });
  }

  async updateCartItem(itemId: string, quantity: number) {
    return this.request<any>(`/cart/items/${itemId}`, {
      method: 'PUT',
      body: JSON.stringify({ quantity }),
    });
  }

  async removeCartItem(itemId: string) {
    return this.request<any>(`/cart/items/${itemId}`, {
      method: 'DELETE',
    });
  }

  async clearCart() {
    return this.request<any>('/cart', { method: 'DELETE' });
  }

  // Orders
  async createOrder(addressId: string, paymentMethod: string = 'cod') {
    return this.request<any>('/orders', {
      method: 'POST',
      body: JSON.stringify({
        address_id: addressId,
        payment_method: paymentMethod,
      }),
    });
  }

  async getOrders() {
    return this.request<any[]>('/orders');
  }

  async getOrder(orderId: string) {
    return this.request<any>(`/orders/${orderId}`);
  }

  async cancelOrder(orderId: string) {
    return this.request<any>(`/orders/${orderId}/cancel`, { method: 'POST' });
  }

  // Returns
  async createReturn(data: {
    order_id: string;
    order_item_id: string;
    reason: string;
    reason_details?: string;
  }) {
    return this.request<any>('/returns', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getReturns() {
    return this.request<any[]>('/returns');
  }

  async getReturn(returnId: string) {
    return this.request<any>(`/returns/${returnId}`);
  }

  async cancelReturn(returnId: string) {
    return this.request<any>(`/returns/${returnId}/cancel`, { method: 'POST' });
  }

  // Reviews
  async getProductReviews(productId: string) {
    return this.request<any[]>(`/reviews/product/${productId}`);
  }

  async getReviewSummary(productId: string) {
    return this.request<any>(`/reviews/product/${productId}/summary`);
  }

  async createReview(data: {
    product_id: string;
    rating: number;
    title?: string;
    content?: string;
    order_id?: string;
  }) {
    return this.request<any>('/reviews', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Wishlist
  async getWishlist() {
    return this.request<any[]>('/wishlist');
  }

  async addToWishlist(productId: string) {
    return this.request<any>(`/wishlist/${productId}`, { method: 'POST' });
  }

  async removeFromWishlist(productId: string) {
    return this.request<any>(`/wishlist/${productId}`, { method: 'DELETE' });
  }

  // Seed
  async seedDatabase() {
    return this.request<any>('/seed', { method: 'POST' });
  }
}

export const api = new ApiClient();
