"use client";

import Link from "next/link";

export default function AuthShell({
  eyebrow,
  title,
  description,
  footer,
  children,
}) {
  return (
    <main className="auth-page">
      <section className="auth-panel auth-panel-accent">
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <p className="auth-copy">{description}</p>
        <div className="auth-notes">
          <div>
            <span className="auth-note-label">JWT</span>
            <span>Stored locally for authenticated requests</span>
          </div>
          <div>
            <span className="auth-note-label">Roles</span>
            <span>`customer`, `maker`, and manually seeded `admin`</span>
          </div>
          <div>
            <span className="auth-note-label">Backend</span>
            <span>{process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"}</span>
          </div>
        </div>
      </section>

      <section className="auth-panel auth-panel-form">
        <div className="auth-header">
          <Link className="auth-home-link" href="/">
            Handcraft Marketplace
          </Link>
        </div>
        {children}
        {footer ? <div className="auth-footer">{footer}</div> : null}
      </section>
    </main>
  );
}
