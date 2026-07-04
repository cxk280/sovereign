import type { Stat } from '../api/types';

export function StatTile({ stat }: { stat: Stat }) {
  return (
    <div className="stat-tile">
      <span className="stat-label">{stat.label}</span>
      <span className="stat-value">{stat.value}</span>
      {stat.delta && <span className={`stat-delta ${stat.tone}`}>{stat.delta}</span>}
    </div>
  );
}
