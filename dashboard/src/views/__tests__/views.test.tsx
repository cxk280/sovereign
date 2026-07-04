import { render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import type { LeaderboardPayload, OverviewPayload } from '../../api/types';
import { Leaderboard } from '../Leaderboard';
import { Overview } from '../Overview';

function mockFetch(payload: unknown) {
  vi.stubGlobal(
    'fetch',
    vi.fn(async () => ({ ok: true, json: async () => payload }) as Response),
  );
}

afterEach(() => vi.unstubAllGlobals());

const OVERVIEW: OverviewPayload = {
  stats: [
    { label: 'MODELS LIVE', value: '1', delta: null, tone: 'neutral' },
    { label: 'REQUESTS / MIN', value: '42', delta: '▲ 12%', tone: 'positive' },
  ],
  requests_series: [1, 2, 3],
  backend: {
    serving: 'Ollama · local',
    model: 'qwen2.5-coder:1.5b',
    quant: 'Q4_K_M',
    readiness: [{ name: 'Gateway', status: 'healthy' }],
    note: null,
  },
};

const LEADERBOARD: LeaderboardPayload = {
  tasks: ['code-gen', 'code-review', 'test-gen'],
  rows: [
    { name: 'qwen2.5-coder:7b', scores: { 'code-gen': 0.92, 'code-review': 0.78, 'test-gen': 0.85 }, overall: 0.85, curated: true },
    { name: 'mistral:7b', scores: { 'code-gen': 0.74, 'code-review': 0.6, 'test-gen': 0.66 }, overall: 0.67, curated: false },
  ],
  note: 'illustrative',
};

describe('Overview', () => {
  it('renders stat tiles and the backend model once loaded', async () => {
    mockFetch(OVERVIEW);
    render(<Overview />);
    expect(await screen.findByText('MODELS LIVE')).toBeInTheDocument();
    expect(screen.getByText('qwen2.5-coder:1.5b')).toBeInTheDocument();
    expect(screen.getByText('Gateway')).toBeInTheDocument();
  });
});

describe('Leaderboard', () => {
  it('renders the ranked table with a curated winner', async () => {
    mockFetch(LEADERBOARD);
    render(<Leaderboard />);
    expect(await screen.findByText('qwen2.5-coder:7b')).toBeInTheDocument();
    expect(screen.getByText('★ curated route · all code tasks')).toBeInTheDocument();
    // overall 0.85 -> 85% (also appears as the test-gen score)
    expect(screen.getAllByText('85%').length).toBeGreaterThan(0);
  });
});
