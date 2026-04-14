"use client";

import Link from "next/link";

export default function MakerPage() {
  return (
    <main className="page">
      <section className="card dashboard-card">
        <p className="eyebrow">Maker Area</p>
        <h1>Maker dashboard</h1>
        <p>This is the maker landing page after authentication.</p>
        <div className="dashboard-actions">
          <Link className="primary-link" href="/home">
            Back to home
          </Link>
        </div>
      </section>
    </main>
  );
}
