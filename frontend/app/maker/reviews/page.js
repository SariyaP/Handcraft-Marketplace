"use client";

import { useEffect, useState } from "react";

import AppShell from "../../../components/ui/AppShell";
import { EmptyState, LoadingState } from "../../../components/ui/StateCard";
import { getLogoutAction, getMakerNav } from "../../../lib/navigation";
import { useRequireRole } from "../../../lib/useRequireRole";
import { fetchMakerReviews } from "../../../lib/reviews";

export default function MakerReviewsPage() {
  const { user, token, isCheckingAuth } = useRequireRole("maker");
  const [reviews, setReviews] = useState([]);
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (isCheckingAuth || !token) {
      return;
    }

    async function loadPage() {
      setIsLoading(true);
      try {
        const data = await fetchMakerReviews(token);
        setReviews(data);
      } catch (error) {
        setErrorMessage(error.message || "Unable to load reviews.");
      } finally {
        setIsLoading(false);
      }
    }

    loadPage();
  }, [isCheckingAuth, token]);

  if (isCheckingAuth || isLoading) {
    return (
      <AppShell
        eyebrow="Maker Reviews"
        title="Customer feedback"
        description="Read reviews on your products and completed commissions."
        navItems={getMakerNav("reviews")}
        actions={getLogoutAction()}
      >
        <section className="card content-card">
          <LoadingState
            title="Loading reviews..."
            description="Fetching customer feedback for your products and commissions."
          />
        </section>
      </AppShell>
    );
  }

  return (
    <AppShell
      eyebrow="Maker Reviews"
      title={user ? `${user.full_name}'s feedback` : "Customer feedback"}
      description="Read customer reviews for your products and completed commissions."
      navItems={getMakerNav("reviews")}
      actions={getLogoutAction()}
    >
      <section className="card content-card maker-dashboard-card">
        <div className="section-header">
          <div>
            <p className="eyebrow">Feedback</p>
            <h2>{user ? `${user.full_name}'s feedback` : "Customer feedback"}</h2>
            <p>Read customer reviews for your products and completed commissions.</p>
          </div>
        </div>

        {errorMessage ? <p className="form-message">{errorMessage}</p> : null}

        {reviews.length === 0 ? (
          <EmptyState
            eyebrow="No Reviews"
            title="No reviews yet"
            description="Customer feedback will appear here."
          />
        ) : (
          <div className="review-list">
            {reviews.map((review) => (
              <article className="review-item" key={review.id}>
                <div className="review-header">
                  <div>
                    <strong>{review.customer_name}</strong>
                    <p>{new Date(review.created_at).toLocaleDateString()}</p>
                  </div>
                  <span className="rating-badge">{review.rating} / 5</span>
                </div>
                <div className="review-meta-row">
                  <span className="order-status">{review.target_type}</span>
                  <strong>
                    {review.target_type === "product"
                      ? review.product_name
                      : review.commission_title}
                  </strong>
                </div>
                <p>{review.comment || "No written comment provided."}</p>
              </article>
            ))}
          </div>
        )}
      </section>
    </AppShell>
  );
}
