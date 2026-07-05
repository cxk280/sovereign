import { useApi } from '../api/client';
import type { OverviewPayload } from '../api/types';
import { AreaChart } from '../components/charts';
import { Card } from '../components/Card';
import { Page } from '../components/Page';
import { StatTile } from '../components/StatTile';

export function Overview() {
  const { data, loading, error } = useApi<OverviewPayload>('/api/overview');
  return (
    <Page title="Overview" loading={loading || !data} error={error}>
      {data && (
        <>
          <div className="stat-row">
            {data.stats.map((s) => (
              <StatTile key={s.label} stat={s} />
            ))}
          </div>
          <div className="row">
            <Card
              className="grow"
              title="Requests — last hour"
              meta={`${data.stats[1].value} req/min now`}
            >
              <AreaChart values={data.requests_series} />
            </Card>
            <Card title="Backend" className="side-card">
              <div className="backend-box">
                <div className="backend-box-head">
                  <span className="dot" />
                  {data.backend.serving} (serving)
                </div>
                <div className="kv">
                  <span className="k">model</span>
                  <span className="v">{data.backend.model}</span>
                </div>
                <div className="kv">
                  <span className="k">quant</span>
                  <span className="v">{data.backend.quant}</span>
                </div>
              </div>
              <div className="readiness-label">READINESS</div>
              {data.backend.readiness.map((r) => (
                <div key={r.name} className="readiness-row">
                  <span className="dot" />
                  {r.name}
                  <span className="status">{r.status}</span>
                </div>
              ))}
              {data.backend.note && <div className="muted-note">{data.backend.note}</div>}
            </Card>
          </div>
        </>
      )}
    </Page>
  );
}
