"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import LogoutButton from "../components/auth/LogoutButton";
import { getRedirectPathForRole, getStoredUser } from "../lib/auth";

export default function LandingPage() {
  const router = useRouter();
  const appName =
    process.env.NEXT_PUBLIC_APP_NAME ?? "Handcraft Marketplace";
  const apiBaseUrl =
    process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
  const [user, setUser] = useState(null);

  useEffect(() => {
    const storedUser = getStoredUser();
    setUser(storedUser);

    if (storedUser?.role) {
      router.replace(getRedirectPathForRole(storedUser.role));
    }
  }, [router]);

  const primaryHref = user ? getRedirectPathForRole(user.role) : "/login";
  const primaryLabel = user ? (user.role === "customer" ? "Open products" : `Open ${user.role} dashboard`) : "Login";

  return (
    <main className="page">
      <section className="card landing-card">
        <p className="eyebrow">Marketplace Access</p>
        <h1>{appName}</h1>
        <p>
          Sign in or create an account to access the FastAPI-backed marketplace.
          The frontend is pointed at <strong>{apiBaseUrl}</strong>.
        </p>
        {user ? (
          <div className="landing-status">
            <span className="landing-status-label">Signed in as</span>
            <strong>{user.full_name}</strong>
            <span>
              {user.email} · {user.role}
            </span>
          </div>
        ) : null}
        <div className="dashboard-actions">
          <Link className="primary-link" href={primaryHref}>
            {primaryLabel}
          </Link>
          <Link className="ghost-link" href="/products">
            Browse products
          </Link>
          {user ? (
            <>
              <LogoutButton />
            </>
          ) : (
            <Link className="ghost-link" href="/register">
              Register
            </Link>
          )}
        </div>
      </section>
    </main>
  );
}
