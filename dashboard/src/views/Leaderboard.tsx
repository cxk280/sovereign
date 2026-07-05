import { useApi } from '../api/client';
import type { LeaderboardPayload } from '../api/types';
import { Card } from '../components/Card';
import { GroupedBarChart } from '../components/charts';
import { Page } from '../components/Page';

const TASK_COLORS = ['var(--indigo)', 'var(--emerald)', 'var(--amber)'];

function pct(x: number): string {
  return `${Math.round(x * 100)}%`;
}

export function Leaderboard() {
  const { data, loading, error } = useApi<LeaderboardPayload>('/api/leaderboard');
  return (
    <Page title="Evaluation leaderboard" loading={loading || !data} error={error}>
      {data && (
        <>
          <div className="page-head">
            <h1 className="page-title">Model leaderboard — code tasks</h1>
            <p className="page-sub">
              Pass rate per model across code-gen, code-review, and test-gen. Benchmarked against a
              Vultr A16.
            </p>
          </div>
          <Card title="Pass rate by task">
            <div className="chart-scroll">
              <GroupedBarChart
                colors={TASK_COLORS}
                seriesLabels={data.tasks}
                groups={data.rows.map((r) => ({
                  label: r.name,
                  values: data.tasks.map((t) => r.scores[t]),
                }))}
              />
            </div>
          </Card>
          <Card>
            <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>MODEL</th>
                  {data.tasks.map((t) => (
                    <th key={t}>{t.toUpperCase()}</th>
                  ))}
                  <th>OVERALL</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {data.rows.map((r) => (
                  <tr key={r.name} className={r.curated ? 'winner' : undefined}>
                    <td className="model">{r.name}</td>
                    {data.tasks.map((t) => (
                      <td key={t}>{pct(r.scores[t])}</td>
                    ))}
                    <td className="overall">{pct(r.overall)}</td>
                    <td>
                      {r.curated && (
                        <span className="pill curated">★ curated route · all code tasks</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            </div>
          </Card>
          {data.note && <p className="muted-note">{data.note}</p>}
        </>
      )}
    </Page>
  );
}
