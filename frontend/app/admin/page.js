"use client";

import Link from "next/link";

export default function AdminPage() {
  return (
    <main className="page">
      <section className="card dashboard-card">
        <p className="eyebrow">Admin Area</p>
        <h1>Admin dashboard</h1>
        <p>This is the admin landing page after authentication.</p>
        <div className="dashboard-actions">
          <Link className="primary-link" href="/home">
            Back to home
          </Link>
        </div>
      </section>
    </main>
  );
}
