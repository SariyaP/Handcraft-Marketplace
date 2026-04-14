"use client";

import Link from "next/link";

export default function CustomerPage() {
  return (
    <main className="page">
      <section className="card dashboard-card">
        <p className="eyebrow">Customer Area</p>
        <h1>Customer dashboard</h1>
        <p>This is the customer landing page after authentication.</p>
        <div className="dashboard-actions">
          <Link className="primary-link" href="/home">
            Back to home
          </Link>
        </div>
      </section>
    </main>
  );
}
