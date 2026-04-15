"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import LogoutButton from "./LogoutButton";
import {
  clearAuthSession,
  fetchCurrentUser,
  fetchRoleDashboard,
  getRedirectPathForRole,
  getStoredToken,
  getStoredUser,
  hasRequiredRole,
  persistAuthSession,
} from "../../lib/auth";

export default function ProtectedRolePage({
  allowedRoles,
  eyebrow,
  title,
  description,
}) {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [dashboardMessage, setDashboardMessage] = useState("");
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

      if (!hasRequiredRole(cachedUser, allowedRoles)) {
        router.replace(getRedirectPathForRole(cachedUser.role));
        return;
      }
    }

    async function loadProtectedPage() {
      try {
        const currentUser = await fetchCurrentUser(token);
        persistAuthSession({
          access_token: token,
          user: currentUser,
        });
        setUser(currentUser);

        if (!hasRequiredRole(currentUser, allowedRoles)) {
          router.replace(getRedirectPathForRole(currentUser.role));
          return;
        }

        const dashboardPayload = await fetchRoleDashboard(currentUser.role, token);
        setDashboardMessage(dashboardPayload.message);
      } catch (error) {
        clearAuthSession();
        setErrorMessage(error.message || "Unable to verify your access.");
        router.replace("/login");
        return;
      } finally {
        setIsLoading(false);
      }
    }

    loadProtectedPage();
  }, [allowedRoles, router]);

  if (isLoading) {
    return (
      <main className="page">
        <section className="card dashboard-card">
          <p className="eyebrow">Loading</p>
          <h1>Checking your access...</h1>
          <p>Verifying your session and role permissions.</p>
        </section>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="page">
        <section className="card dashboard-card">
          <p className="eyebrow">Access Error</p>
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
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <p>{dashboardMessage || description}</p>
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
          <LogoutButton />
        </div>
      </section>
    </main>
  );
}
