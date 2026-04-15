"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import AppShell from "../../components/ui/AppShell";
import { EmptyState, LoadingState } from "../../components/ui/StateCard";
import { getCustomerNav, getLogoutAction } from "../../lib/navigation";
import { useRequireRole } from "../../lib/useRequireRole";
import { fetchWishlist, removeWishlistItem } from "../../lib/products";

export default function WishlistPage() {
  const { user, token, isCheckingAuth } = useRequireRole("customer");
  const [items, setItems] = useState([]);
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [busyProductId, setBusyProductId] = useState(null);

  useEffect(() => {
    if (isCheckingAuth || !token) {
      return;
    }

    async function loadPage() {
      setIsLoading(true);
      try {
        const wishlistItems = await fetchWishlist(token);
        setItems(wishlistItems);
      } catch (error) {
        setErrorMessage(error.message || "Unable to load wishlist.");
      } finally {
        setIsLoading(false);
      }
    }

    loadPage();
  }, [isCheckingAuth, token]);

  async function handleRemove(productId) {
    if (!token) {
      return;
    }

    setBusyProductId(productId);
    setErrorMessage("");

    try {
      await removeWishlistItem(productId, token);
      setItems((current) => current.filter((item) => item.product_id !== productId));
    } catch (error) {
      setErrorMessage(error.message || "Unable to remove wishlist item.");
    } finally {
      setBusyProductId(null);
    }
  }

  if (isCheckingAuth || isLoading) {
    return (
      <AppShell
        eyebrow="Wishlist"
        title="Saved products"
        description="Your saved handmade items."
        navItems={getCustomerNav("wishlist")}
        actions={getLogoutAction()}
      >
        <section className="card content-card">
          <LoadingState title="Loading wishlist..." description="Fetching your saved products." />
        </section>
      </AppShell>
    );
  }

  return (
    <AppShell
      eyebrow="Wishlist"
      title={user ? `${user.full_name}'s saved products` : "Saved products"}
      description="Review products you saved and return to the catalog when ready."
      navItems={getCustomerNav("wishlist")}
      actions={getLogoutAction()}
    >
      <section className="card content-card products-page-card">
        <div className="section-header">
          <div>
            <p className="eyebrow">Saved Items</p>
            <h2>Wishlist overview</h2>
            <p>Review products you saved and jump back into the catalog when you are ready.</p>
          </div>
        </div>

        {errorMessage ? <p className="form-message">{errorMessage}</p> : null}

        {items.length === 0 ? (
          <EmptyState
            eyebrow="No Wishlist Items"
            title="Your wishlist is empty"
            description="Browse products and save the ones you want to revisit."
          />
        ) : (
          <section className="product-grid">
            {items.map((item) => (
              <article className="product-card product-card-elevated" key={item.id}>
                <div className="product-image-placeholder" aria-hidden="true">
                  <span>Handcraft</span>
                </div>
                <div className="product-card-body">
                  <div className="product-card-heading">
                    <h2>{item.product_name}</h2>
                    <span className="product-price">${Number(item.price).toFixed(2)}</span>
                  </div>
                  <p>{item.product_description || "No description available yet."}</p>
                  <div className="product-meta">
                    <span>Maker</span>
                    <strong>
                      <Link href={`/maker/${item.maker_id}`}>{item.maker_name}</Link>
                    </strong>
                  </div>
                  <div className="dashboard-actions">
                    <Link className="primary-link" href={`/products/${item.product_id}`}>
                      View details
                    </Link>
                    <button
                      className="ghost-button wishlist-button-active"
                      type="button"
                      onClick={() => handleRemove(item.product_id)}
                      disabled={busyProductId === item.product_id}
                    >
                      {busyProductId === item.product_id ? "Removing..." : "Remove"}
                    </button>
                  </div>
                </div>
              </article>
            ))}
          </section>
        )}
      </section>
    </AppShell>
  );
}
