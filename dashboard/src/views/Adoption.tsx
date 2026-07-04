import { useApi } from '../api/client';
import type { AdoptionPayload } from '../api/types';
import { BarChart } from '../components/charts';
import { Card } from '../components/Card';
import { Page } from '../components/Page';
import { StatTile } from '../components/StatTile';

const SURFACE_COLOR: Record<string, string> = {
  indigo: 'var(--indigo)',
  emerald: 'var(--emerald)',
  sky: 'var(--sky)',
};

export function Adoption() {
  const { data, loading, error } = useApi<AdoptionPayload>('/api/adoption');
  return (
    <Page title="Adoption & impact" loading={loading || !data} error={error}>
      {data && (
        <>
          <div className="page-head">
            <h1 className="page-title">Adoption &amp; impact</h1>
            <p className="page-sub">
              Usage, acceptance, and estimated time saved across IDE, CLI, and CI — last 30 days.
            </p>
          </div>
          <div className="stat-row">
            {data.stats.map((s) => (
              <StatTile key={s.label} stat={s} />
            ))}
          </div>
          <div className="row">
            <Card className="grow" title="Requests by day" meta="last 30 days">
              <BarChart values={data.usage_series} />
            </Card>
            <Card title="By surface" style={{ width: 380, flexShrink: 0 }}>
              {data.by_surface.map((s) => (
                <div key={s.label} className="surface">
                  <div className="surface-head">
                    {s.label}
                    <span className="pct">{s.pct}%</span>
                  </div>
                  <div className="surface-track">
                    <div
                      className="surface-fill"
                      style={{ width: `${s.pct}%`, background: SURFACE_COLOR[s.color] }}
                    />
                  </div>
                </div>
              ))}
              <div className="muted-note">
                IDE tab-autocomplete + chat drives most volume; CI runs AI review, test-gen, and MR
                summaries on every MR.
              </div>
            </Card>
          </div>
        </>
      )}
    </Page>
  );
}
