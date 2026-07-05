import { Link } from 'react-router-dom';
import { Page } from '../components/Page';

export function NotFound() {
  return (
    <Page title="Not found" loading={false} error={null}>
      <div className="notfound">
        <div className="notfound-code">404</div>
        <h1 className="page-title">Page not found</h1>
        <p className="page-sub">That route doesn’t exist in the operator dashboard.</p>
        <Link className="btn-link" to="/">
          ← Back to Overview
        </Link>
      </div>
    </Page>
  );
}
