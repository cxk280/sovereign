import type { ReactNode } from 'react';
import { Topbar } from './Topbar';

export function Page({
  title,
  loading,
  error,
  children,
}: {
  title: string;
  loading: boolean;
  error: string | null;
  children: ReactNode;
}) {
  return (
    <>
      <Topbar title={title} />
      <div className="content">
        {loading ? (
          <div className="state">Loading…</div>
        ) : error ? (
          <div className="state error">Failed to load: {error}</div>
        ) : (
          children
        )}
      </div>
    </>
  );
}
