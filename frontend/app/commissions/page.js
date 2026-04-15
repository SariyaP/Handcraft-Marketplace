"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import AppShell from "../../components/ui/AppShell";
import { EmptyState, LoadingState } from "../../components/ui/StateCard";
import { getCustomerNav, getLogoutAction } from "../../lib/navigation";
import { useRequireRole } from "../../lib/useRequireRole";
import { createCommission, fetchCustomerCommissions } from "../../lib/commissions";
import { createCommissionReview } from "../../lib/reviews";

const initialValues = {
  maker_id: "",
  title: "",
  description: "",
  customization_notes: "",
  budget: "",
};

export default function CommissionsPage() {
  const { user, token, isCheckingAuth } = useRequireRole("customer");
  const [values, setValues] = useState(initialValues);
  const [commissions, setCommissions] = useState([]);
  const [reviewDrafts, setReviewDrafts] = useState({});
  const [message, setMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submittingReviewId, setSubmittingReviewId] = useState(null);

  useEffect(() => {
    const prefilledMakerId =
      typeof window !== "undefined"
        ? new URLSearchParams(window.location.search).get("makerId")
        : null;
    if (prefilledMakerId) {
      setValues((current) => ({
        ...current,
        maker_id: prefilledMakerId,
      }));
    }
  }, []);

  useEffect(() => {
    if (isCheckingAuth || !token) {
      return;
    }

    async function loadPage() {
      setIsLoading(true);
      try {
        const data = await fetchCustomerCommissions(token);
        setCommissions(data);
      } catch (error) {
        setErrorMessage(error.message || "Unable to load commissions.");
      } finally {
        setIsLoading(false);
      }
    }

    loadPage();
  }, [isCheckingAuth, token]);

  function handleChange(event) {
    const { name, value } = event.target;
    setValues((current) => ({
      ...current,
      [name]: value,
    }));
  }

  function handleReviewChange(commissionId, field, value) {
    setReviewDrafts((current) => ({
      ...current,
      [commissionId]: {
        rating: current[commissionId]?.rating || "5",
        comment: current[commissionId]?.comment || "",
        ...current[commissionId],
        [field]: value,
      },
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (!token) {
      return;
    }

    setIsSubmitting(true);
    setMessage("");
    setErrorMessage("");

    try {
      const created = await createCommission(token, {
        maker_id: Number(values.maker_id),
        title: values.title,
        description: values.description || null,
        customization_notes: values.customization_notes || null,
        budget: values.budget ? Number(values.budget) : null,
      });
      setCommissions((current) => [created, ...current]);
      setValues((current) => ({
        ...initialValues,
        maker_id: current.maker_id,
      }));
      setMessage("Commission request submitted.");
    } catch (error) {
      setErrorMessage(error.message || "Unable to submit commission request.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleReviewSubmit(event, commissionId) {
    event.preventDefault();
    if (!token) {
      return;
    }

    const draft = reviewDrafts[commissionId] || { rating: "5", comment: "" };
    setSubmittingReviewId(commissionId);
    setErrorMessage("");
    setMessage("");

    try {
      await createCommissionReview(commissionId, token, {
        rating: Number(draft.rating),
        comment: draft.comment || null,
      });
      setCommissions((current) =>
        current.map((commission) =>
          commission.id === commissionId ? { ...commission, has_review: true } : commission
        )
      );
      setReviewDrafts((current) => ({
        ...current,
        [commissionId]: {
          rating: "5",
          comment: "",
        },
      }));
      setMessage("Commission review submitted.");
    } catch (error) {
      setErrorMessage(error.message || "Unable to submit commission review.");
    } finally {
      setSubmittingReviewId(null);
    }
  }

  if (isCheckingAuth || isLoading) {
    return (
      <AppShell
        eyebrow="Commissions"
        title="Customer requests"
        description="Request custom work from makers and track progress."
        navItems={getCustomerNav("commissions")}
        actions={getLogoutAction()}
      >
        <section className="card content-card">
          <LoadingState title="Loading commissions..." description="Fetching your commission requests." />
        </section>
      </AppShell>
    );
  }

  return (
    <AppShell
      eyebrow="Commissions"
      title={user ? `${user.full_name}'s requests` : "Commission requests"}
      description="Request custom work from makers and track each request from submission to completion."
      navItems={getCustomerNav("commissions")}
      actions={getLogoutAction()}
    >
      <section className="card content-card maker-dashboard-card">
        <div className="section-header">
          <div>
            <p className="eyebrow">Custom Work</p>
            <h2>{user ? `${user.full_name}'s commission requests` : "Commission requests"}</h2>
            <p>Request custom work from makers and track the status of each request.</p>
          </div>
        </div>

        {message ? <p className="form-message form-message-success">{message}</p> : null}
        {errorMessage ? <p className="form-message">{errorMessage}</p> : null}

        <div className="maker-dashboard-layout">
          <section className="maker-panel">
            <p className="eyebrow">New Request</p>
            <h2>Create commission request</h2>
            <form className="maker-form" onSubmit={handleSubmit}>
              <label className="form-field" htmlFor="maker_id">
                <span>Maker ID</span>
                <input
                  id="maker_id"
                  name="maker_id"
                  type="number"
                  min="1"
                  className="form-input"
                  value={values.maker_id}
                  onChange={handleChange}
                  required
                  disabled={isSubmitting}
                />
              </label>
              <label className="form-field" htmlFor="title">
                <span>Project title</span>
                <input
                  id="title"
                  name="title"
                  className="form-input"
                  value={values.title}
                  onChange={handleChange}
                  required
                  disabled={isSubmitting}
                />
              </label>
              <label className="form-field" htmlFor="description">
                <span>Project description</span>
                <textarea
                  id="description"
                  name="description"
                  className="form-input maker-textarea"
                  rows={4}
                  value={values.description}
                  onChange={handleChange}
                  disabled={isSubmitting}
                />
              </label>
              <label className="form-field" htmlFor="customization_notes">
                <span>Customization notes</span>
                <textarea
                  id="customization_notes"
                  name="customization_notes"
                  className="form-input maker-textarea"
                  rows={4}
                  value={values.customization_notes}
                  onChange={handleChange}
                  disabled={isSubmitting}
                />
              </label>
              <label className="form-field" htmlFor="budget">
                <span>Budget</span>
                <input
                  id="budget"
                  name="budget"
                  type="number"
                  min="0"
                  step="0.01"
                  className="form-input"
                  value={values.budget}
                  onChange={handleChange}
                  disabled={isSubmitting}
                />
              </label>
              <button className="form-submit" type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Submitting..." : "Submit request"}
              </button>
            </form>
          </section>

          <section className="maker-panel">
            <p className="eyebrow">Your Requests</p>
            <h2>Commission history</h2>
            {commissions.length === 0 ? (
              <EmptyState
                eyebrow="No Requests"
                title="No commissions yet"
                description="Submit a request to get started."
              />
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
                        <span>Maker</span>
                        <strong>{commission.maker_name}</strong>
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
                    {commission.status === "completed" ? (
                      commission.has_review ? (
                        <div className="progress-item">
                          <strong>Review submitted</strong>
                          <p>You already left feedback for this completed commission.</p>
                        </div>
                      ) : (
                        <form
                          className="maker-form review-form"
                          onSubmit={(event) => handleReviewSubmit(event, commission.id)}
                        >
                          <strong>Leave feedback</strong>
                          <div className="maker-form-grid">
                            <label className="form-field" htmlFor={`commission-rating-${commission.id}`}>
                              <span>Rating</span>
                              <select
                                id={`commission-rating-${commission.id}`}
                                className="form-input"
                                value={reviewDrafts[commission.id]?.rating || "5"}
                                onChange={(event) =>
                                  handleReviewChange(commission.id, "rating", event.target.value)
                                }
                                disabled={submittingReviewId === commission.id}
                              >
                                {[5, 4, 3, 2, 1].map((value) => (
                                  <option key={value} value={value}>
                                    {value} / 5
                                  </option>
                                ))}
                              </select>
                            </label>
                            <label className="form-field" htmlFor={`commission-comment-${commission.id}`}>
                              <span>Comment</span>
                              <textarea
                                id={`commission-comment-${commission.id}`}
                                className="form-input maker-textarea"
                                rows={3}
                                value={reviewDrafts[commission.id]?.comment || ""}
                                onChange={(event) =>
                                  handleReviewChange(commission.id, "comment", event.target.value)
                                }
                                disabled={submittingReviewId === commission.id}
                                placeholder="Share feedback about the completed commission."
                              />
                            </label>
                          </div>
                          <button
                            className="form-submit"
                            type="submit"
                            disabled={submittingReviewId === commission.id}
                          >
                            {submittingReviewId === commission.id ? "Submitting..." : "Submit review"}
                          </button>
                        </form>
                      )
                    ) : null}
                  </article>
                ))}
              </div>
            )}
          </section>
        </div>
      </section>
    </AppShell>
  );
}
