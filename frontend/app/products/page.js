"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import AppShell from "../../components/ui/AppShell";
import { EmptyState, LoadingState } from "../../components/ui/StateCard";
import {
  clearAuthSession,
  fetchCurrentUser,
  getStoredToken,
  getStoredUser,
  hasRequiredRole,
  persistAuthSession,
} from "../../lib/auth";
import {
  addWishlistItem,
  fetchCustomerDashboard,
  fetchProducts,
  fetchWishlist,
  removeWishlistItem,
} from "../../lib/products";

const initialFilters = {
  minPrice: "",
  maxPrice: "",
  makerId: "",
};

function ProductCard({
  product,
  canWishlist,
  isWishlisted,
  onToggleWishlist,
  wishlistBusyId,
}) {
  return (
    <article className="product-card product-card-elevated">
      <div className="product-image-placeholder" aria-hidden="true">
        <span>Handcraft</span>
      </div>
      <div className="product-card-body">
        <div className="product-card-heading">
          <h2>{product.name}</h2>
          <span className="product-price">${Number(product.price).toFixed(2)}</span>
        </div>
        <p>{product.description || "No description available yet."}</p>
        <div className="product-meta">
          <span>Maker</span>
          <strong>
            <Link href={`/maker/${product.maker_id}`}>{product.maker_name}</Link>
          </strong>
        </div>
        <Link className="primary-link" href={`/products/${product.id}`}>
          View details
        </Link>
        {canWishlist ? (
          <button
            className={isWishlisted ? "ghost-button wishlist-button-active" : "ghost-button"}
            type="button"
            onClick={() => onToggleWishlist(product.id)}
            disabled={wishlistBusyId === product.id}
          >
            {wishlistBusyId === product.id
              ? "Saving..."
              : isWishlisted
                ? "Remove from wishlist"
                : "Add to wishlist"}
          </button>
        ) : null}
      </div>
    </article>
  );
}

function CustomerDashboardTab({ dashboard, isDashboardLoading, dashboardError, user }) {
  if (!user) {
    return (
      <EmptyState
        eyebrow="Sign In Required"
        title="Your orders are private"
        description="Sign in as a customer to view ordered items and progress updates."
      />
    );
  }

  if (isDashboardLoading) {
    return (
      <LoadingState
        title="Loading your orders..."
        description="Fetching ordered items and their progress updates."
      />
    );
  }

  if (dashboardError) {
    return (
      <EmptyState eyebrow="Orders Error" title="Unable to load your orders" description={dashboardError} />
    );
  }

  if (!dashboard.orders.length) {
    return (
      <EmptyState
        eyebrow="No Orders"
        title="You do not have any customer orders yet"
        description="Browse products and place an order to track each item and its progress here."
      />
    );
  }

  return (
    <section className="orders-list">
      {dashboard.orders.map((order) => (
        <article className="order-card" key={order.id}>
          <div className="order-card-header">
            <div>
              <p className="eyebrow">Order #{order.id}</p>
              <h2>{order.product_name}</h2>
            </div>
            <span className="order-status">{order.status}</span>
          </div>
          <p>{order.product_description || "No description provided for this ordered item."}</p>
          <div className="user-summary">
            <div>
              <span>Maker</span>
              <strong>{order.maker_name}</strong>
            </div>
            <div>
              <span>Quantity</span>
              <strong>{order.quantity}</strong>
            </div>
            <div>
              <span>Order value</span>
              <strong>${Number(order.total_price).toFixed(2)}</strong>
            </div>
            <div>
              <span>Updated</span>
              <strong>{new Date(order.updated_at).toLocaleDateString()}</strong>
            </div>
          </div>
          <div className="selection-list">
            {order.selections.map((selection) => (
              <div className="selection-item" key={`${order.id}-${selection.option_name}`}>
                <span>{selection.option_name}</span>
                <strong>{selection.choice_label}</strong>
              </div>
            ))}
          </div>
          <div className="progress-list">
            {order.progress_updates.length ? (
              order.progress_updates.map((update) => (
                <div className="progress-item" key={update.id}>
                  <strong>{new Date(update.created_at).toLocaleDateString()}</strong>
                  <p>{update.message}</p>
                </div>
              ))
            ) : (
              <div className="progress-item">
                <strong>No progress yet</strong>
                <p>The maker has not posted any progress updates for this item yet.</p>
              </div>
            )}
          </div>
        </article>
      ))}
    </section>
  );
}

export default function ProductsPage() {
  const [filters, setFilters] = useState(initialFilters);
  const [products, setProducts] = useState([]);
  const [errorMessage, setErrorMessage] = useState("");
  const [isProductsLoading, setIsProductsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("products");
  const [user, setUser] = useState(null);
  const [dashboard, setDashboard] = useState({ orders: [] });
  const [dashboardError, setDashboardError] = useState("");
  const [isDashboardLoading, setIsDashboardLoading] = useState(false);
  const [wishlistIds, setWishlistIds] = useState([]);
  const [wishlistBusyId, setWishlistBusyId] = useState(null);

  useEffect(() => {
    loadProducts(initialFilters);
  }, []);

  useEffect(() => {
    const token = getStoredToken();
    const cachedUser = getStoredUser();

    if (!token || !cachedUser || !hasRequiredRole(cachedUser, ["customer"])) {
      return;
    }

    setUser(cachedUser);
    loadCustomerDashboard(token);
    loadWishlist(token);

    async function refreshCustomer() {
      try {
        const currentUser = await fetchCurrentUser(token);
        persistAuthSession({
          access_token: token,
          user: currentUser,
        });
        setUser(currentUser);
      } catch {
        clearAuthSession();
        setUser(null);
      }
    }

    refreshCustomer();
  }, []);

  function handleChange(event) {
    const { name, value } = event.target;
    setFilters((current) => ({
      ...current,
      [name]: value,
    }));
  }

  async function loadProducts(nextFilters) {
    setIsProductsLoading(true);
    setErrorMessage("");

    try {
      const data = await fetchProducts(nextFilters);
      setProducts(data);
    } catch (error) {
      setErrorMessage(error.message || "Unable to load products.");
    } finally {
      setIsProductsLoading(false);
    }
  }

  async function loadCustomerDashboard(token) {
    setIsDashboardLoading(true);
    setDashboardError("");

    try {
      const data = await fetchCustomerDashboard(token);
      setDashboard(data);
    } catch (error) {
      setDashboardError(error.message || "Unable to load customer dashboard.");
    } finally {
      setIsDashboardLoading(false);
    }
  }

  async function loadWishlist(token) {
    try {
      const items = await fetchWishlist(token);
      setWishlistIds(items.map((item) => item.product_id));
    } catch {
      setWishlistIds([]);
    }
  }

  async function handleToggleWishlist(productId) {
    const token = getStoredToken();
    if (!token || !user || !hasRequiredRole(user, ["customer"])) {
      return;
    }

    setWishlistBusyId(productId);
    setErrorMessage("");

    try {
      if (wishlistIds.includes(productId)) {
        await removeWishlistItem(productId, token);
        setWishlistIds((current) => current.filter((id) => id !== productId));
      } else {
        await addWishlistItem(productId, token);
        setWishlistIds((current) => [...current, productId]);
      }
    } catch (error) {
      setErrorMessage(error.message || "Unable to update wishlist.");
    } finally {
      setWishlistBusyId(null);
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();
    await loadProducts(filters);
  }

  async function handleReset() {
    setFilters(initialFilters);
    await loadProducts(initialFilters);
  }

  const navItems = user && hasRequiredRole(user, ["customer"])
    ? [
        { href: "/products", label: "Marketplace", caption: "Browse and order", active: true },
        { href: "/wishlist", label: "Wishlist", caption: "Saved items" },
        { href: "/commissions", label: "Commissions", caption: "Custom requests" },
      ]
    : [
        { href: "/products", label: "Marketplace", caption: "Public catalog", active: true },
        { href: "/login", label: "Login", caption: "Customer or maker access" },
        { href: "/register", label: "Register", caption: "Create an account" },
      ];

  const shellActions = user
    ? [{ type: "logout", redirectTo: "/login" }]
    : [{ href: "/login", label: "Login", className: "primary-link sidebar-action-button" }];

  return (
    <AppShell
      eyebrow="Marketplace"
      title={user ? `Welcome back, ${user.full_name}` : "Handcraft Marketplace"}
      description={
        user && hasRequiredRole(user, ["customer"])
          ? "Browse products, manage saved items, and switch to your order tracking tab."
          : "Browse handmade listings, compare prices, and explore makers."
      }
      navItems={navItems}
      actions={shellActions}
    >
      <section className="card content-card products-page-card">
        <div className="section-header">
          <div>
            <p className="eyebrow">Catalog</p>
            <h2>{activeTab === "products" ? "Product browsing" : "Order tracking"}</h2>
            <p>
              {user && hasRequiredRole(user, ["customer"])
                ? "Browse products or switch to your orders tab to track ordered items and their progress."
                : "Browse handmade listings and filter by price or maker."}
            </p>
          </div>
        </div>

        {user && hasRequiredRole(user, ["customer"]) ? (
          <div className="tab-bar" role="tablist" aria-label="Customer marketplace sections">
            <button
              className={activeTab === "products" ? "tab-button tab-button-active" : "tab-button"}
              type="button"
              onClick={() => setActiveTab("products")}
            >
              Products
            </button>
            <button
              className={activeTab === "dashboard" ? "tab-button tab-button-active" : "tab-button"}
              type="button"
              onClick={() => setActiveTab("dashboard")}
            >
              My orders
            </button>
          </div>
        ) : null}

        {activeTab === "products" ? (
          <>
            <form className="products-filter-bar" onSubmit={handleSubmit}>
              <label className="form-field" htmlFor="minPrice">
                <span>Min price</span>
                <input
                  id="minPrice"
                  name="minPrice"
                  type="number"
                  min="0"
                  step="0.01"
                  value={filters.minPrice}
                  onChange={handleChange}
                  className="form-input"
                />
              </label>
              <label className="form-field" htmlFor="maxPrice">
                <span>Max price</span>
                <input
                  id="maxPrice"
                  name="maxPrice"
                  type="number"
                  min="0"
                  step="0.01"
                  value={filters.maxPrice}
                  onChange={handleChange}
                  className="form-input"
                />
              </label>
              <label className="form-field" htmlFor="makerId">
                <span>Maker ID</span>
                <input
                  id="makerId"
                  name="makerId"
                  type="number"
                  min="1"
                  step="1"
                  value={filters.makerId}
                  onChange={handleChange}
                  className="form-input"
                />
              </label>
              <div className="products-filter-actions">
                <button className="form-submit" type="submit" disabled={isProductsLoading}>
                  {isProductsLoading ? "Loading..." : "Apply filters"}
                </button>
                <button
                  className="ghost-button"
                  type="button"
                  onClick={handleReset}
                  disabled={isProductsLoading}
                >
                  Reset
                </button>
              </div>
            </form>

            {errorMessage ? <p className="form-message">{errorMessage}</p> : null}

            {isProductsLoading ? (
              <LoadingState title="Loading products..." description="Fetching listings from the backend." />
            ) : products.length === 0 ? (
              <EmptyState
                eyebrow="No Results"
                title="No products found"
                description="Try adjusting the filters or seed some products in the backend."
              />
            ) : (
              <section className="product-grid">
                {products.map((product) => (
                  <ProductCard
                    key={product.id}
                    product={product}
                    canWishlist={Boolean(user && hasRequiredRole(user, ["customer"]))}
                    isWishlisted={wishlistIds.includes(product.id)}
                    onToggleWishlist={handleToggleWishlist}
                    wishlistBusyId={wishlistBusyId}
                  />
                ))}
              </section>
            )}
          </>
        ) : (
          <CustomerDashboardTab
            dashboard={dashboard}
            isDashboardLoading={isDashboardLoading}
            dashboardError={dashboardError}
            user={user}
          />
        )}
      </section>
    </AppShell>
  );
}
