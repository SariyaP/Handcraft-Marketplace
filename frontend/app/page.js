export default function HomePage() {
  const appName =
    process.env.NEXT_PUBLIC_APP_NAME ?? "Handcraft Marketplace";
  const apiBaseUrl =
    process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

  return (
    <main className="page">
      <section className="card">
        <p className="eyebrow">Project scaffold</p>
        <h1>{appName}</h1>
        <p>
          Next.js App Router and JavaScript are ready. Connect frontend work to
          <strong> {apiBaseUrl}</strong> when feature development begins.
        </p>
      </section>
    </main>
  );
}
