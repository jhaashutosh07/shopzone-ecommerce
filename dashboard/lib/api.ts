const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface LoginResponse {
  access_token: string;
  token_type: string;
}

interface DashboardStats {
  total_returns: number;
  approved_returns: number;
  denied_returns: number;
  pending_returns: number;
  approval_rate: number;
  avg_score: number;
  total_buyers: number;
  high_risk_buyers: number;
  total_products: number;
  high_return_products: number;
  returns_this_week: number;
  returns_last_week: number;
}

interface ReturnRequest {
  id: string;
  buyer_id: string;
  product_id: string;
  order_id: string;
  order_date: string;
  order_amount: number;
  request_date: string;
  reason: string;
  eligibility_score: number | null;
  risk_level: string | null;
  risk_flags: Array<{ code: string; description: string; severity: string }>;
  decision: string;
  days_since_order: number;
}

interface Buyer {
  id: string;
  external_buyer_id: string;
  total_orders: number;
  total_returns: number;
  avg_review_score: number;
  return_rate: number;
  created_at: string;
}

class ApiClient {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', token);
    }
  }

  getToken(): string | null {
    if (this.token) return this.token;
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('token');
    }
    return this.token;
  }

  clearToken() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
    }
  }

  private async fetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = this.getToken();
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_URL}/api/v1${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      if (response.status === 401) {
        this.clearToken();
        if (typeof window !== 'undefined') {
          window.location.href = '/';
        }
      }
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || 'Request failed');
    }

    return response.json();
  }

  async login(email: string, password: string): Promise<LoginResponse> {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${API_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    this.setToken(data.access_token);
    return data;
  }

  async register(name: string, email: string, password: string): Promise<void> {
    await this.fetch('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, password }),
    });
  }

  async getMe(): Promise<any> {
    return this.fetch('/auth/me');
  }

  async generateApiKey(): Promise<{ api_key: string }> {
    return this.fetch('/auth/api-key', { method: 'POST' });
  }

  async getDashboardStats(): Promise<DashboardStats> {
    return this.fetch('/dashboard/stats');
  }

  async getReturns(page = 1, perPage = 20, decision?: string): Promise<{
    items: ReturnRequest[];
    total: number;
    page: number;
    per_page: number;
  }> {
    let url = `/returns?page=${page}&per_page=${perPage}`;
    if (decision) url += `&decision=${decision}`;
    return this.fetch(url);
  }

  async updateReturnDecision(returnId: string, decision: string): Promise<ReturnRequest> {
    return this.fetch(`/returns/${returnId}`, {
      method: 'PUT',
      body: JSON.stringify({ decision }),
    });
  }

  async getBuyers(page = 1, perPage = 20): Promise<Buyer[]> {
    return this.fetch(`/buyers?page=${page}&per_page=${perPage}`);
  }

  async updateSettings(settings: {
    default_return_window?: number;
    fraud_threshold?: number;
    auto_approve_threshold?: number;
  }): Promise<void> {
    await this.fetch('/auth/me', {
      method: 'PUT',
      body: JSON.stringify(settings),
    });
  }
}

export const api = new ApiClient();
export type { DashboardStats, ReturnRequest, Buyer };
