import Link from "next/link";

export default function HomePage() {
  const appName =
    process.env.NEXT_PUBLIC_APP_NAME ?? "Handcraft Marketplace";
  const apiBaseUrl =
    process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

  return (
    <main className="page">
      <section className="card">
        <p className="eyebrow">Authentication Ready</p>
        <h1>{appName}</h1>
        <p>
          FastAPI auth is wired to <strong>{apiBaseUrl}</strong>. Sign in,
          register, or open the authenticated home screen.
        </p>
        <div className="dashboard-actions">
          <Link className="primary-link" href="/login">
            Login
          </Link>
          <Link className="ghost-link" href="/register">
            Register
          </Link>
          <Link className="ghost-link" href="/home">
            Home
          </Link>
        </div>
      </section>
    </main>
  );
}
