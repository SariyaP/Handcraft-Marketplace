export function LoadingState({ title, description }) {
  return (
    <div className="state-card">
      <div className="loading-dots" aria-hidden="true">
        <span />
        <span />
        <span />
      </div>
      <p className="eyebrow">Loading</p>
      <h2>{title}</h2>
      <p>{description}</p>
    </div>
  );
}

export function EmptyState({ eyebrow, title, description }) {
  return (
    <div className="state-card state-card-empty">
      {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
      <h2>{title}</h2>
      <p>{description}</p>
    </div>
  );
}
