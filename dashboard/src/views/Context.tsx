import { useApi } from '../api/client';
import type { ContextPayload } from '../api/types';
import { Card } from '../components/Card';
import { Icon } from '../components/icons';
import { Page } from '../components/Page';

const ICON_BG: Record<string, string> = {
  indigo: 'var(--indigo-50)',
  emerald: 'var(--emerald-50)',
  amber: 'var(--amber-50)',
  violet: 'var(--indigo-50)',
};
const ICON_FG: Record<string, string> = {
  indigo: 'var(--indigo)',
  emerald: 'var(--emerald)',
  amber: 'var(--amber)',
  violet: 'var(--violet)',
};

export function Context() {
  const { data, loading, error } = useApi<ContextPayload>('/api/context');
  return (
    <Page title="Context browser" loading={loading || !data} error={error}>
      {data && (
        <>
          <div className="page-head">
            <h1 className="page-title">Context browser</h1>
            <p className="page-sub">
              Explore the indexed internal knowledge served to the MCP and RAG layers. Read-only.
            </p>
          </div>
          <div className="row">
            <Card
              title="Indexed sources"
              meta={`${data.total_chunks} chunks · updated ${data.updated}`}
              className="side-card"
            >
              {data.sources.map((s) => (
                <div key={s.name} className="source-row">
                  <span
                    className="icon-square"
                    style={{ background: ICON_BG[s.color], color: ICON_FG[s.color] }}
                  >
                    <Icon name={s.icon} />
                  </span>
                  <div className="grow">
                    <div className="source-name">{s.name}</div>
                    <div className="source-path">
                      {s.path} · {s.docs_label}
                    </div>
                  </div>
                  <div className="source-count">
                    <div className="n">{s.chunks}</div>
                    <div className="u">chunks</div>
                  </div>
                </div>
              ))}
            </Card>
            <Card className="grow" title="Retrieval preview">
              <p className="preview-caption">
                A sample query and the top grounded chunks the RAG layer returns — an
                illustrative, read-only preview (not a live search in this build).
              </p>
              <label className="search-box">
                <Icon name="search" />
                <input
                  className="query"
                  value={data.query}
                  readOnly
                  aria-label="Example retrieval query (read-only preview)"
                />
                <span className="hint">example · top {data.results.length}</span>
              </label>
              {data.results.map((r) => (
                <div key={r.path} className="result-card">
                  <div className="result-head">
                    <span className="result-title">{r.title}</span>
                    <span className="score-badge">score {r.score.toFixed(2)}</span>
                  </div>
                  <span className="result-path">{r.path}</span>
                  <span className="result-snippet">{r.snippet}</span>
                </div>
              ))}
            </Card>
          </div>
        </>
      )}
    </Page>
  );
}
