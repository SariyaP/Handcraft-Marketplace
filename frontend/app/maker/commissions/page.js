"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import LogoutButton from "../../../components/auth/LogoutButton";
import {
  clearAuthSession,
  fetchCurrentUser,
  getStoredToken,
  getStoredUser,
  hasRequiredRole,
  persistAuthSession,
} from "../../../lib/auth";
import {
  createCommissionWipUpdate,
  fetchMakerCommissions,
  updateCommissionStatus,
} from "../../../lib/commissions";

const statusOptions = ["pending", "accepted", "rejected", "in_progress", "completed"];

export default function MakerCommissionsPage() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [commissions, setCommissions] = useState([]);
  const [errorMessage, setErrorMessage] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState(null);
  const [wipDrafts, setWipDrafts] = useState({});
  const [postingUpdateId, setPostingUpdateId] = useState(null);

  useEffect(() => {
    const token = getStoredToken();
    const cachedUser = getStoredUser();

    if (!token || !cachedUser) {
      router.replace("/login");
      return;
    }

    if (!hasRequiredRole(cachedUser, ["maker"])) {
      router.replace("/products");
      return;
    }

    async function loadPage() {
      try {
        const currentUser = await fetchCurrentUser(token);
        if (!hasRequiredRole(currentUser, ["maker"])) {
          router.replace("/products");
          return;
        }

        persistAuthSession({
          access_token: token,
          user: currentUser,
        });
        setUser(currentUser);

        const data = await fetchMakerCommissions(token);
        setCommissions(data);
      } catch (error) {
        clearAuthSession();
        setErrorMessage(error.message || "Unable to load incoming commissions.");
        router.replace("/login");
      } finally {
        setIsLoading(false);
      }
    }

    loadPage();
  }, [router]);

  async function handleStatusChange(commissionId, nextStatus) {
    const token = getStoredToken();
    if (!token) {
      router.replace("/login");
      return;
    }

    setUpdatingId(commissionId);
    setMessage("");
    setErrorMessage("");

    try {
      const updated = await updateCommissionStatus(commissionId, token, nextStatus);
      setCommissions((current) =>
        current.map((commission) =>
          commission.id === commissionId ? updated : commission
        )
      );
      setMessage("Commission status updated.");
    } catch (error) {
      setErrorMessage(error.message || "Unable to update commission status.");
    } finally {
      setUpdatingId(null);
    }
  }

  function handleWipChange(commissionId, field, value) {
    setWipDrafts((current) => ({
      ...current,
      [commissionId]: {
        message: current[commissionId]?.message || "",
        image_url: current[commissionId]?.image_url || "",
        ...current[commissionId],
        [field]: value,
      },
    }));
  }

  async function handlePostUpdate(event, commissionId) {
    event.preventDefault();

    const token = getStoredToken();
    if (!token) {
      router.replace("/login");
      return;
    }

    const draft = wipDrafts[commissionId] || { message: "", image_url: "" };
    setPostingUpdateId(commissionId);
    setMessage("");
    setErrorMessage("");

    try {
      const created = await createCommissionWipUpdate(commissionId, token, {
        message: draft.message,
        image_url: draft.image_url || null,
      });
      setCommissions((current) =>
        current.map((commission) =>
          commission.id === commissionId
            ? { ...commission, wip_updates: [created, ...(commission.wip_updates || [])] }
            : commission
        )
      );
      setWipDrafts((current) => ({
        ...current,
        [commissionId]: { message: "", image_url: "" },
      }));
      setMessage("WIP update posted.");
    } catch (error) {
      setErrorMessage(error.message || "Unable to post WIP update.");
    } finally {
      setPostingUpdateId(null);
    }
  }

  if (isLoading) {
    return (
      <main className="page">
        <section className="card dashboard-card">
          <p className="eyebrow">Loading</p>
          <h1>Loading incoming commissions...</h1>
          <p>Fetching requests from customers.</p>
        </section>
      </main>
    );
  }

  return (
    <main className="page">
      <section className="card maker-dashboard-card">
        <div className="products-header">
          <div>
            <p className="eyebrow">Maker Commissions</p>
            <h1>{user ? `${user.full_name}'s commission inbox` : "Incoming commissions"}</h1>
            <p>Review customer requests, accept or reject them, and update progress status.</p>
          </div>
          <div className="dashboard-actions">
            <Link className="ghost-link" href="/maker">
              Back to dashboard
            </Link>
            <LogoutButton />
          </div>
        </div>

        {message ? <p className="form-message form-message-success">{message}</p> : null}
        {errorMessage ? <p className="form-message">{errorMessage}</p> : null}

        <section className="maker-panel">
          <p className="eyebrow">Incoming Requests</p>
          <h2>Customer commissions</h2>
          {commissions.length === 0 ? (
            <div className="products-empty-state">
              <p>No incoming commissions yet.</p>
            </div>
          ) : (
            <div className="maker-product-list">
              {commissions.map((commission) => (
                <article className="maker-product-item" key={commission.id}>
                  <div className="maker-product-header">
                    <div>
                      <h3>{commission.title}</h3>
                      <p>{commission.description || "No description provided."}</p>
                    </div>
                    <span className="order-status">{commission.status}</span>
                  </div>
                  <div className="user-summary">
                    <div>
                      <span>Customer</span>
                      <strong>{commission.customer_name}</strong>
                    </div>
                    <div>
                      <span>Budget</span>
                      <strong>{commission.budget ? `$${Number(commission.budget).toFixed(2)}` : "Not set"}</strong>
                    </div>
                    <div>
                      <span>Updated</span>
                      <strong>{new Date(commission.updated_at).toLocaleDateString()}</strong>
                    </div>
                  </div>
                  <div className="progress-item">
                    <strong>Customization notes</strong>
                    <p>{commission.customization_notes || "No customization notes provided."}</p>
                  </div>
                  <label className="form-field" htmlFor={`status-${commission.id}`}>
                    <span>Update status</span>
                    <select
                      id={`status-${commission.id}`}
                      className="form-input"
                      value={commission.status}
                      onChange={(event) => handleStatusChange(commission.id, event.target.value)}
                      disabled={updatingId === commission.id}
                    >
                      {statusOptions.map((status) => (
                        <option key={status} value={status}>
                          {status}
                        </option>
                      ))}
                    </select>
                  </label>
                  <form
                    className="maker-form review-form"
                    onSubmit={(event) => handlePostUpdate(event, commission.id)}
                  >
                    <strong>Post WIP update</strong>
                    <label className="form-field" htmlFor={`wip-message-${commission.id}`}>
                      <span>Update message</span>
                      <textarea
                        id={`wip-message-${commission.id}`}
                        className="form-input maker-textarea"
                        rows={3}
                        value={wipDrafts[commission.id]?.message || ""}
                        onChange={(event) =>
                          handleWipChange(commission.id, "message", event.target.value)
                        }
                        disabled={postingUpdateId === commission.id}
                        required
                      />
                    </label>
                    <label className="form-field" htmlFor={`wip-image-${commission.id}`}>
                      <span>Image URL</span>
                      <input
                        id={`wip-image-${commission.id}`}
                        className="form-input"
                        value={wipDrafts[commission.id]?.image_url || ""}
                        onChange={(event) =>
                          handleWipChange(commission.id, "image_url", event.target.value)
                        }
                        disabled={postingUpdateId === commission.id}
                        placeholder="https://example.com/progress-image.jpg"
                      />
                    </label>
                    <button
                      className="form-submit"
                      type="submit"
                      disabled={postingUpdateId === commission.id}
                    >
                      {postingUpdateId === commission.id ? "Posting..." : "Post update"}
                    </button>
                  </form>
                  {commission.wip_updates?.length ? (
                    <div className="progress-list">
                      {commission.wip_updates.map((update) => (
                        <div className="progress-item" key={update.id}>
                          <strong>{new Date(update.created_at).toLocaleDateString()}</strong>
                          <p>{update.message}</p>
                          {update.image_url ? (
                            <Link href={update.image_url} target="_blank">
                              View image
                            </Link>
                          ) : null}
                        </div>
                      ))}
                    </div>
                  ) : null}
                </article>
              ))}
            </div>
          )}
        </section>
      </section>
    </main>
  );
}
