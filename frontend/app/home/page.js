"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import {
  clearAuthSession,
  fetchCurrentUser,
  getRedirectPathForRole,
  getStoredToken,
  getStoredUser,
  persistAuthSession,
} from "../../lib/auth";

export default function HomePage() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = getStoredToken();
    const cachedUser = getStoredUser();

    if (!token) {
      router.replace("/login");
      return;
    }

    if (cachedUser) {
      setUser(cachedUser);
    }

    async function loadCurrentUser() {
      try {
        const currentUser = await fetchCurrentUser(token);
        setUser(currentUser);
        persistAuthSession({
          access_token: token,
          user: currentUser,
        });
      } catch (error) {
        clearAuthSession();
        setErrorMessage(error.message || "Unable to load your account.");
        router.replace("/login");
        return;
      } finally {
        setIsLoading(false);
      }
    }

    loadCurrentUser();
  }, [router]);

  function handleLogout() {
    clearAuthSession();
    router.replace("/login");
  }

  if (isLoading) {
    return (
      <main className="page">
        <section className="card dashboard-card">
          <p className="eyebrow">Loading</p>
          <h1>Checking your session...</h1>
          <p>Fetching the current user from the API.</p>
        </section>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="page">
        <section className="card dashboard-card">
          <p className="eyebrow">Session Error</p>
          <h1>Authentication required</h1>
          <p>{errorMessage || "Please sign in again."}</p>
          <div className="dashboard-actions">
            <Link className="ghost-link" href="/login">
              Go to login
            </Link>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main className="page">
      <section className="card dashboard-card">
        <p className="eyebrow">Authenticated</p>
        <h1>Hello, {user.full_name}</h1>
        <p>
          You are signed in as <strong>{user.role}</strong>. Use the role
          dashboard below or sign out.
        </p>
        <div className="user-summary">
          <div>
            <span>Email</span>
            <strong>{user.email}</strong>
          </div>
          <div>
            <span>Role</span>
            <strong>{user.role}</strong>
          </div>
          <div>
            <span>Status</span>
            <strong>{user.is_active ? "Active" : "Inactive"}</strong>
          </div>
        </div>
        <div className="dashboard-actions">
          <Link className="primary-link" href={getRedirectPathForRole(user.role)}>
            Open {user.role} dashboard
          </Link>
          <button className="ghost-button" type="button" onClick={handleLogout}>
            Log Out
          </button>
        </div>
      </section>
    </main>
  );
}
