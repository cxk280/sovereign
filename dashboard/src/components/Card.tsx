import type { CSSProperties, ReactNode } from 'react';

export function Card({
  title,
  meta,
  headExtra,
  children,
  className,
  style,
}: {
  title?: string;
  meta?: string;
  headExtra?: ReactNode;
  children: ReactNode;
  className?: string;
  style?: CSSProperties;
}) {
  return (
    <div className={`card${className ? ` ${className}` : ''}`} style={style}>
      {(title || meta || headExtra) && (
        <div className="card-head">
          {title && <span className="card-title">{title}</span>}
          {headExtra}
          {meta && <span className="card-meta">{meta}</span>}
        </div>
      )}
      {children}
    </div>
  );
}
