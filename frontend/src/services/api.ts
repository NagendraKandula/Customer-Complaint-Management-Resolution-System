import axios, { AxiosError } from 'axios';

export const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? '';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 20000,
  headers: { Accept: 'application/json' },
});

export function errorMessage(e: unknown): string {
  if (axios.isAxiosError(e)) {
    const err = e as AxiosError<any>;
    if (err.code === 'ERR_NETWORK' || !err.response) {
      return 'Cannot reach the backend. Check that FastAPI is running and that CORS allows this origin.';
    }
    const detail = err.response.data?.detail;
    const text = typeof detail === 'string' ? detail : detail ? JSON.stringify(detail) : err.message;
    return `${err.response.status}: ${text}`;
  }
  return e instanceof Error ? e.message : 'Something went wrong.';
}

export async function getJson<T = any>(url: string, params?: Record<string, unknown>): Promise<T> {
  const res = await api.get<T>(url, { params });
  return res.data;
}

export const checkHealth = () => getJson('/api/health');
