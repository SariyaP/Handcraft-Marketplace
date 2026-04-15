"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import AppShell from "../../../components/ui/AppShell";
import { EmptyState, LoadingState } from "../../../components/ui/StateCard";
import {
  clearAuthSession,
  fetchCurrentUser,
  getStoredToken,
  getStoredUser,
  hasRequiredRole,
  persistAuthSession,
} from "../../../lib/auth";
import { fetchMakerReviews } from "../../../lib/reviews";

export default function MakerReviewsPage() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);

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

        const data = await fetchMakerReviews(token);
        setReviews(data);
      } catch (error) {
        clearAuthSession();
        setErrorMessage(error.message || "Unable to load reviews.");
        router.replace("/login");
      } finally {
        setIsLoading(false);
      }
    }

    loadPage();
  }, [router]);

  if (isLoading) {
    return (
      <AppShell
        eyebrow="Maker Reviews"
        title="Customer feedback"
        description="Read reviews on your products and completed commissions."
        navItems={[
          { href: "/maker", label: "Products", caption: "Catalog management" },
          { href: "/maker/profile", label: "Profile", caption: "Shop details" },
          { href: "/maker/commissions", label: "Commissions", caption: "Requests and WIP" },
          { href: "/maker/reviews", label: "Reviews", caption: "Customer feedback", active: true },
        ]}
        actions={[{ type: "logout", redirectTo: "/login" }]}
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
      navItems={[
        { href: "/maker", label: "Products", caption: "Catalog management" },
        { href: "/maker/profile", label: "Profile", caption: "Shop details" },
        { href: "/maker/commissions", label: "Commissions", caption: "Requests and WIP" },
        { href: "/maker/reviews", label: "Reviews", caption: "Customer feedback", active: true },
      ]}
      actions={[{ type: "logout", redirectTo: "/login" }]}
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
