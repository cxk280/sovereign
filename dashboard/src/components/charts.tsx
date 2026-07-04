// Hand-rolled SVG charts — no charting dependency, so output matches the Figma
// mocks pixel-for-pixel. Each measures its container for a crisp 1:1 viewBox.
import { type RefObject, useLayoutEffect, useRef, useState } from 'react';

function useWidth(): [RefObject<HTMLDivElement>, number] {
  const ref = useRef<HTMLDivElement>(null);
  const [w, setW] = useState(0);
  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    const ro = new ResizeObserver((entries) => {
      for (const e of entries) setW(e.contentRect.width);
    });
    ro.observe(el);
    setW(el.clientWidth);
    return () => ro.disconnect();
  }, []);
  return [ref, w];
}

export function AreaChart({ values, height = 180 }: { values: number[]; height?: number }) {
  const [ref, w] = useWidth();
  const max = Math.max(...values) * 1.2;
  const n = values.length;
  const pts = values.map((v, i) => [(i / (n - 1)) * w, height - (v / max) * height]);
  const line = pts.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' ');
  const area =
    `M0 ${height} ` +
    pts.map((p) => `L${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' ') +
    ` L${w} ${height} Z`;
  return (
    <div ref={ref} style={{ width: '100%' }}>
      {w > 0 && (
        <svg width={w} height={height} role="img" aria-label="Requests over time">
          <defs>
            <linearGradient id="area-grad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stopColor="var(--indigo)" stopOpacity="0.2" />
              <stop offset="1" stopColor="var(--indigo)" stopOpacity="0" />
            </linearGradient>
          </defs>
          <path d={area} fill="url(#area-grad)" />
          <path
            d={line}
            fill="none"
            stroke="var(--indigo)"
            strokeWidth={2.5}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      )}
    </div>
  );
}

export function BarChart({ values, height = 200 }: { values: number[]; height?: number }) {
  const [ref, w] = useWidth();
  const max = Math.max(...values) * 1.05;
  const n = values.length;
  const gap = 6;
  const bw = (w - gap * (n - 1)) / n;
  return (
    <div ref={ref} style={{ width: '100%' }}>
      {w > 0 && (
        <svg width={w} height={height} role="img" aria-label="Requests by day">
          {values.map((v, i) => {
            const bh = (v / max) * height;
            return (
              <rect
                key={i}
                x={i * (bw + gap)}
                y={height - bh}
                width={bw}
                height={bh}
                rx={2.5}
                fill="var(--indigo)"
              />
            );
          })}
        </svg>
      )}
    </div>
  );
}

export interface Group {
  label: string;
  values: number[];
}

export function GroupedBarChart({
  groups,
  colors,
  height = 300,
}: {
  groups: Group[];
  colors: string[];
  height?: number;
}) {
  const [ref, w] = useWidth();
  const padB = 30;
  const padL = 36;
  const plotH = height - padB;
  const plotW = w - padL;
  const gw = plotW / groups.length;
  const series = colors.length;
  const barW = Math.min(32, (gw - 16) / series);
  const inner = barW * series + 6 * (series - 1);
  return (
    <div ref={ref} style={{ width: '100%' }}>
      {w > 0 && (
        <svg width={w} height={height} role="img" aria-label="Pass rate by task">
          {[0, 1, 2, 3, 4].map((t) => {
            const yy = plotH - (t / 4) * plotH;
            return (
              <g key={t}>
                <line x1={padL} y1={yy} x2={w} y2={yy} stroke="var(--border-subtle)" strokeWidth={1} />
                <text x={padL - 8} y={yy + 4} textAnchor="end" fontSize={11} fill="var(--text-muted)">
                  {(t / 4).toFixed(2)}
                </text>
              </g>
            );
          })}
          {groups.map((grp, i) => {
            const gx = padL + i * gw + (gw - inner) / 2;
            return (
              <g key={grp.label}>
                {grp.values.map((val, j) => {
                  const bh = val * plotH;
                  const x = gx + j * (barW + 6);
                  const y = plotH - bh;
                  return (
                    <g key={j}>
                      <rect x={x} y={y} width={barW} height={bh} rx={3} fill={colors[j]} />
                      <text
                        x={x + barW / 2}
                        y={y - 6}
                        textAnchor="middle"
                        fontSize={11}
                        fontWeight={600}
                        fill="var(--text-secondary)"
                      >
                        {val.toFixed(2)}
                      </text>
                    </g>
                  );
                })}
                <text
                  x={padL + i * gw + gw / 2}
                  y={height - 8}
                  textAnchor="middle"
                  fontSize={12.5}
                  fill="var(--text-primary)"
                >
                  {grp.label}
                </text>
              </g>
            );
          })}
        </svg>
      )}
    </div>
  );
}
