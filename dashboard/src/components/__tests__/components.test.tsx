import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { Sidebar } from '../Sidebar';
import { StatTile } from '../StatTile';
import { StatusPill } from '../StatusPill';

describe('StatTile', () => {
  it('renders label, value, and toned delta', () => {
    render(<StatTile stat={{ label: 'REQUESTS / MIN', value: '42', delta: '▲ 12%', tone: 'positive' }} />);
    expect(screen.getByText('REQUESTS / MIN')).toBeInTheDocument();
    expect(screen.getByText('42')).toBeInTheDocument();
    expect(screen.getByText('▲ 12%')).toHaveClass('stat-delta', 'positive');
  });
});

describe('StatusPill', () => {
  it('applies the status as a class', () => {
    render(<StatusPill status="candidate" />);
    const pill = screen.getByText('candidate');
    expect(pill).toHaveClass('pill', 'candidate');
  });
});

describe('Sidebar', () => {
  it('renders all five nav items and marks the active route', () => {
    render(
      <MemoryRouter initialEntries={['/registry']}>
        <Sidebar />
      </MemoryRouter>,
    );
    for (const label of ['Overview', 'Registry', 'Leaderboard', 'Adoption', 'Context']) {
      expect(screen.getByText(label)).toBeInTheDocument();
    }
    expect(screen.getByText('Registry').closest('a')).toHaveClass('active');
  });
});
