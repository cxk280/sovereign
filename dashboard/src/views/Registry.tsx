import { useApi } from '../api/client';
import type { RegistryPayload } from '../api/types';
import { Card } from '../components/Card';
import { Page } from '../components/Page';
import { StatusPill } from '../components/StatusPill';

export function Registry() {
  const { data, loading, error } = useApi<RegistryPayload>('/api/registry');
  return (
    <Page title="Model registry" loading={loading || !data} error={error}>
      {data && (
        <>
          <div className="page-head">
            <h1 className="page-title">Registered models</h1>
            <p className="page-sub">
              Versions, quantization, serving backend, and task routing — curated from the eval
              leaderboard.
            </p>
          </div>
          <Card>
            <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>MODEL</th>
                  <th>VERSION</th>
                  <th>QUANT</th>
                  <th>TASKS</th>
                  <th>BACKEND</th>
                  <th>STATUS</th>
                </tr>
              </thead>
              <tbody>
                {data.models.map((m) => (
                  <tr key={m.name}>
                    <td className="model">{m.name}</td>
                    <td>{m.version}</td>
                    <td>{m.quantization}</td>
                    <td>{m.tasks.join(' · ')}</td>
                    <td>{m.backend}</td>
                    <td>
                      <StatusPill status={m.status} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            </div>
          </Card>
          <Card title="Active routing" meta="read-only in this build">
            <div className="route-grid">
              {data.routing.map((r) => (
                <div key={r.task} className="route-card">
                  <span className="route-task">{r.task}</span>
                  <span className="route-arrow">routes to</span>
                  <span className="route-model">{r.model}</span>
                  <span className="route-backend">{r.backend}</span>
                </div>
              ))}
            </div>
          </Card>
        </>
      )}
    </Page>
  );
}
