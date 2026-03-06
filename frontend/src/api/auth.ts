import { apiPost, apiGet } from './client';

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export function login(email: string, password: string) {
  return apiPost<TokenResponse>('/auth/login', { email, password });
}

export function register(email: string, password: string, full_name?: string) {
  return apiPost<User>('/auth/register', { email, password, full_name });
}

export function getMe() {
  return apiGet<User>('/auth/me');
}
