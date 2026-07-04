// Tiny fetch client + a loading/error hook. The base URL is empty by default so
// requests hit relative /api/* (proxied by Vite in dev, by nginx in the image);
// override with VITE_API_BASE for a split deployment.
import { useEffect, useState } from 'react';

const BASE = import.meta.env.VITE_API_BASE ?? '';

export async function fetchJson<T>(path: string, signal?: AbortSignal): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { signal });
  if (!res.ok) throw new Error(`${path} → ${res.status}`);
  return (await res.json()) as T;
}

export interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export function useApi<T>(path: string): AsyncState<T> {
  const [state, setState] = useState<AsyncState<T>>({ data: null, loading: true, error: null });
  useEffect(() => {
    const ctrl = new AbortController();
    setState({ data: null, loading: true, error: null });
    fetchJson<T>(path, ctrl.signal)
      .then((data) => setState({ data, loading: false, error: null }))
      .catch((err: unknown) => {
        if (ctrl.signal.aborted) return;
        setState({ data: null, loading: false, error: err instanceof Error ? err.message : 'error' });
      });
    return () => ctrl.abort();
  }, [path]);
  return state;
}
