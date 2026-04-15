"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

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
  createMakerProduct,
  deleteMakerProduct,
  fetchMakerProducts,
  updateMakerProduct,
} from "../../lib/products";

const initialFormValues = {
  title: "",
  description: "",
  price: "",
  stock_quantity: "",
  is_active: true,
};

function ProductForm({
  values,
  isSubmitting,
  submitLabel,
  onChange,
  onSubmit,
  onCancel,
  showCancel,
}) {
  return (
    <form className="maker-form" onSubmit={onSubmit}>
      <label className="form-field" htmlFor="title">
        <span>Product name</span>
        <input
          id="title"
          name="title"
          className="form-input"
          value={values.title}
          onChange={onChange}
          required
          disabled={isSubmitting}
        />
      </label>
      <label className="form-field" htmlFor="description">
        <span>Description</span>
        <textarea
          id="description"
          name="description"
          className="form-input maker-textarea"
          value={values.description}
          onChange={onChange}
          rows={4}
          disabled={isSubmitting}
        />
      </label>
      <div className="maker-form-grid">
        <label className="form-field" htmlFor="price">
          <span>Price</span>
          <input
            id="price"
            name="price"
            type="number"
            min="0"
            step="0.01"
            className="form-input"
            value={values.price}
            onChange={onChange}
            required
            disabled={isSubmitting}
          />
        </label>
        <label className="form-field" htmlFor="stock_quantity">
          <span>Stock</span>
          <input
            id="stock_quantity"
            name="stock_quantity"
            type="number"
            min="0"
            step="1"
            className="form-input"
            value={values.stock_quantity}
            onChange={onChange}
            required
            disabled={isSubmitting}
          />
        </label>
      </div>
      <label className="maker-checkbox">
        <input
          type="checkbox"
          name="is_active"
          checked={values.is_active}
          onChange={onChange}
          disabled={isSubmitting}
        />
        <span>Product is active</span>
      </label>
      <div className="dashboard-actions">
        <button className="form-submit" type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Saving..." : submitLabel}
        </button>
        {showCancel ? (
          <button className="ghost-button" type="button" onClick={onCancel} disabled={isSubmitting}>
            Cancel edit
          </button>
        ) : null}
      </div>
    </form>
  );
}

export default function MakerPage() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [products, setProducts] = useState([]);
  const [formValues, setFormValues] = useState(initialFormValues);
  const [editingProductId, setEditingProductId] = useState(null);
  const [message, setMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isDeletingId, setIsDeletingId] = useState(null);

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

    setUser(cachedUser);
    async function loadDashboard() {
      setIsLoading(true);
      setErrorMessage("");

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

        const makerProducts = await fetchMakerProducts(token);
        setProducts(makerProducts);
      } catch (error) {
        clearAuthSession();
        setErrorMessage(error.message || "Unable to load the maker dashboard.");
        router.replace("/login");
      } finally {
        setIsLoading(false);
      }
    }

    loadDashboard();
  }, [router]);

  function handleChange(event) {
    const { name, value, type, checked } = event.target;
    setFormValues((current) => ({
      ...current,
      [name]: type === "checkbox" ? checked : value,
    }));
  }

  function resetForm() {
    setFormValues(initialFormValues);
    setEditingProductId(null);
  }

  function startEdit(product) {
    setEditingProductId(product.id);
    setFormValues({
      title: product.title,
      description: product.description || "",
      price: product.price,
      stock_quantity: product.stock_quantity,
      is_active: product.is_active,
    });
    setMessage("");
    setErrorMessage("");
  }

  async function handleSubmit(event) {
    event.preventDefault();
    const token = getStoredToken();
    if (!token) {
      router.replace("/login");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage("");
    setMessage("");

    const payload = {
      title: formValues.title,
      description: formValues.description,
      price: Number(formValues.price),
      stock_quantity: Number(formValues.stock_quantity),
      is_active: formValues.is_active,
    };

    try {
      if (editingProductId) {
        await updateMakerProduct(editingProductId, token, payload);
        setMessage("Product updated.");
      } else {
        await createMakerProduct(token, payload);
        setMessage("Product created.");
      }

      resetForm();
      const makerProducts = await fetchMakerProducts(token);
      setProducts(makerProducts);
    } catch (error) {
      setErrorMessage(error.message || "Unable to save this product.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDelete(productId) {
    const token = getStoredToken();
    if (!token) {
      router.replace("/login");
      return;
    }

    setIsDeletingId(productId);
    setErrorMessage("");
    setMessage("");

    try {
      await deleteMakerProduct(productId, token);
      setProducts((current) => current.filter((product) => product.id !== productId));
      if (editingProductId === productId) {
        resetForm();
      }
      setMessage("Product removed.");
    } catch (error) {
      setErrorMessage(error.message || "Unable to delete this product.");
    } finally {
      setIsDeletingId(null);
    }
  }

  if (isLoading) {
    return (
      <AppShell
        eyebrow="Maker Dashboard"
        title="Maker workspace"
        description="Manage products and shop activity."
        navItems={[
          { href: "/maker", label: "Products", caption: "Catalog management", active: true },
          { href: "/maker/profile", label: "Profile", caption: "Shop details" },
          { href: "/maker/commissions", label: "Commissions", caption: "Requests and WIP" },
          { href: "/maker/reviews", label: "Reviews", caption: "Customer feedback" },
        ]}
        actions={[{ type: "logout", redirectTo: "/login" }]}
      >
        <section className="card content-card">
          <LoadingState
            title="Loading maker dashboard..."
            description="Fetching your products and profile."
          />
        </section>
      </AppShell>
    );
  }

  return (
    <AppShell
      eyebrow="Maker Dashboard"
      title={user ? `${user.full_name}'s workspace` : "Maker workspace"}
      description="Create listings, keep your catalog updated, and manage your shop."
      navItems={[
        { href: "/maker", label: "Products", caption: "Catalog management", active: true },
        { href: "/maker/profile", label: "Profile", caption: "Shop details" },
        { href: "/maker/commissions", label: "Commissions", caption: "Requests and WIP" },
        { href: "/maker/reviews", label: "Reviews", caption: "Customer feedback" },
      ]}
      actions={[{ type: "logout", redirectTo: "/login" }]}
    >
      <section className="card content-card maker-dashboard-card">
        <div className="section-header">
          <div>
            <p className="eyebrow">Catalog</p>
            <h2>{user ? `${user.full_name}'s products` : "Manage your catalog"}</h2>
            <p>Create, edit, and remove products in your maker storefront.</p>
          </div>
        </div>

        {message ? <p className="form-message form-message-success">{message}</p> : null}
        {errorMessage ? <p className="form-message">{errorMessage}</p> : null}

        <div className="maker-dashboard-layout">
          <section className="maker-panel">
            <p className="eyebrow">{editingProductId ? "Edit Product" : "Create Product"}</p>
            <h2>{editingProductId ? "Update listing" : "New listing"}</h2>
            <ProductForm
              values={formValues}
              isSubmitting={isSubmitting}
              submitLabel={editingProductId ? "Update product" : "Create product"}
              onChange={handleChange}
              onSubmit={handleSubmit}
              onCancel={resetForm}
              showCancel={Boolean(editingProductId)}
            />
          </section>

          <section className="maker-panel">
            <p className="eyebrow">Your Products</p>
            <h2>Current catalog</h2>
            {products.length === 0 ? (
              <EmptyState
                eyebrow="No Products"
                title="No products yet"
                description="Create your first listing from the form."
              />
            ) : (
              <div className="maker-product-list">
                {products.map((product) => (
                  <article className="maker-product-item" key={product.id}>
                    <div className="maker-product-header">
                      <div>
                        <h3>{product.title}</h3>
                        <p>{product.description || "No description provided."}</p>
                      </div>
                      <span className={product.is_active ? "order-status" : "maker-status-muted"}>
                        {product.is_active ? "active" : "inactive"}
                      </span>
                    </div>
                    <div className="user-summary">
                      <div>
                        <span>Price</span>
                        <strong>${Number(product.price).toFixed(2)}</strong>
                      </div>
                      <div>
                        <span>Stock</span>
                        <strong>{product.stock_quantity}</strong>
                      </div>
                      <div>
                        <span>Updated</span>
                        <strong>{new Date(product.updated_at).toLocaleDateString()}</strong>
                      </div>
                    </div>
                    <div className="dashboard-actions">
                      <button
                        className="ghost-button"
                        type="button"
                        onClick={() => startEdit(product)}
                        disabled={isDeletingId === product.id}
                      >
                        Edit
                      </button>
                      <button
                        className="ghost-button maker-delete-button"
                        type="button"
                        onClick={() => handleDelete(product.id)}
                        disabled={isDeletingId === product.id}
                      >
                        {isDeletingId === product.id ? "Deleting..." : "Delete"}
                      </button>
                    </div>
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
