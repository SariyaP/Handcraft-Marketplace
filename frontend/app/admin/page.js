"use client";

import { useEffect, useState } from "react";

import AppShell from "../../components/ui/AppShell";
import { LoadingState } from "../../components/ui/StateCard";
import { getAdminNav, getLogoutAction } from "../../lib/navigation";
import { useRequireRole } from "../../lib/useRequireRole";
import {
  fetchAdminProducts,
  fetchAdminReviews,
  fetchAdminUsers,
  fetchAdminVerifications,
  removeAdminProduct,
  removeAdminReview,
  updateAdminUser,
  updateAdminVerification,
} from "../../lib/admin";

export default function AdminPage() {
  const { user, token, isCheckingAuth } = useRequireRole("admin");
  const [users, setUsers] = useState([]);
  const [products, setProducts] = useState([]);
  const [verifications, setVerifications] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [verificationDrafts, setVerificationDrafts] = useState({});
  const [message, setMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [activeAction, setActiveAction] = useState("");

  useEffect(() => {
    if (isCheckingAuth || !token) {
      return;
    }

    async function loadDashboard() {
      setIsLoading(true);
      try {
        const [allUsers, allProducts, allVerifications, allReviews] = await Promise.all([
          fetchAdminUsers(token),
          fetchAdminProducts(token),
          fetchAdminVerifications(token),
          fetchAdminReviews(token),
        ]);

        setUsers(allUsers);
        setProducts(allProducts);
        setVerifications(allVerifications);
        setReviews(allReviews);
        setVerificationDrafts(
          Object.fromEntries(
            allVerifications.map((item) => [
              item.maker_id,
              {
                status: item.status,
                notes: item.notes || "",
              },
            ])
          )
        );
      } catch (error) {
        setErrorMessage(error.message || "Unable to load the admin dashboard.");
      } finally {
        setIsLoading(false);
      }
    }

    loadDashboard();
  }, [isCheckingAuth, token]);

  function handleVerificationChange(makerId, field, value) {
    setVerificationDrafts((current) => ({
      ...current,
      [makerId]: {
        status: current[makerId]?.status || "pending",
        notes: current[makerId]?.notes || "",
        ...current[makerId],
        [field]: value,
      },
    }));
  }

  async function handleVerificationSave(makerId) {
    if (!token) {
      return;
    }

    setActiveAction(`verification-${makerId}`);
    setMessage("");
    setErrorMessage("");

    try {
      const updated = await updateAdminVerification(makerId, token, verificationDrafts[makerId]);
      setVerifications((current) =>
        current.map((item) => (item.maker_id === makerId ? updated : item))
      );
      setVerificationDrafts((current) => ({
        ...current,
        [makerId]: {
          status: updated.status,
          notes: updated.notes || "",
        },
      }));
      setMessage("Verification updated.");
    } catch (error) {
      setErrorMessage(error.message || "Unable to update verification.");
    } finally {
      setActiveAction("");
    }
  }

  async function handleUserStatusToggle(managedUser) {
    if (!token) {
      return;
    }

    setActiveAction(`user-${managedUser.id}`);
    setMessage("");
    setErrorMessage("");

    try {
      const updated = await updateAdminUser(managedUser.id, token, {
        is_active: !managedUser.is_active,
      });
      setUsers((current) =>
        current.map((item) => (item.id === managedUser.id ? updated : item))
      );
      setMessage("User status updated.");
    } catch (error) {
      setErrorMessage(error.message || "Unable to update user status.");
    } finally {
      setActiveAction("");
    }
  }

  async function handleRemoveProduct(productId) {
    if (!token) {
      return;
    }

    setActiveAction(`product-${productId}`);
    setMessage("");
    setErrorMessage("");

    try {
      await removeAdminProduct(productId, token);
      setProducts((current) =>
        current.map((item) => (item.id === productId ? { ...item, is_active: false } : item))
      );
      setMessage("Product removed from the public catalog.");
    } catch (error) {
      setErrorMessage(error.message || "Unable to remove product.");
    } finally {
      setActiveAction("");
    }
  }

  async function handleRemoveReview(reviewId) {
    if (!token) {
      return;
    }

    setActiveAction(`review-${reviewId}`);
    setMessage("");
    setErrorMessage("");

    try {
      await removeAdminReview(reviewId, token);
      setReviews((current) => current.filter((item) => item.id !== reviewId));
      setMessage("Review removed.");
    } catch (error) {
      setErrorMessage(error.message || "Unable to remove review.");
    } finally {
      setActiveAction("");
    }
  }

  if (isCheckingAuth || isLoading) {
    return (
      <AppShell
        eyebrow="Admin Dashboard"
        title="Marketplace moderation"
        description="Review users, products, verifications, and reviews."
        navItems={getAdminNav("moderation")}
        actions={getLogoutAction()}
      >
        <section className="card content-card">
          <LoadingState title="Loading admin dashboard..." description="Fetching moderation data." />
        </section>
      </AppShell>
    );
  }

  return (
    <AppShell
      eyebrow="Admin Dashboard"
      title={user ? `${user.full_name}'s moderation console` : "Marketplace moderation"}
      description="Review users, products, verification requests, and customer feedback."
      navItems={getAdminNav("moderation")}
      actions={getLogoutAction()}
    >
      <section className="card content-card maker-dashboard-card admin-dashboard-card">
        <div className="section-header">
          <div>
            <p className="eyebrow">Moderation</p>
            <h2>{user ? `${user.full_name}'s moderation console` : "Marketplace moderation"}</h2>
            <p>Review users, products, verification requests, and customer feedback.</p>
          </div>
        </div>

        {message ? <p className="form-message form-message-success">{message}</p> : null}
        {errorMessage ? <p className="form-message">{errorMessage}</p> : null}

        <section className="admin-section">
          <div className="admin-section-heading">
            <div>
              <p className="eyebrow">Users</p>
              <h2>All users</h2>
            </div>
          </div>
          <div className="admin-table-wrap">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Joined</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {users.map((item) => (
                  <tr key={item.id}>
                    <td>{item.id}</td>
                    <td>{item.full_name}</td>
                    <td>{item.email}</td>
                    <td>{item.role}</td>
                    <td>{item.is_active ? "active" : "inactive"}</td>
                    <td>{new Date(item.created_at).toLocaleDateString()}</td>
                    <td>
                      <button
                        className="ghost-button"
                        type="button"
                        disabled={activeAction === `user-${item.id}`}
                        onClick={() => handleUserStatusToggle(item)}
                      >
                        {activeAction === `user-${item.id}`
                          ? "Saving..."
                          : item.is_active
                            ? "Deactivate"
                            : "Activate"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="admin-section">
          <div className="admin-section-heading">
            <div>
              <p className="eyebrow">Products</p>
              <h2>All products</h2>
            </div>
          </div>
          <div className="admin-table-wrap">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Product</th>
                  <th>Maker</th>
                  <th>Price</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {products.map((item) => (
                  <tr key={item.id}>
                    <td>{item.id}</td>
                    <td>
                      <strong>{item.title}</strong>
                      <div className="admin-cell-muted">{item.description || "No description"}</div>
                    </td>
                    <td>{item.maker_name}</td>
                    <td>${Number(item.price).toFixed(2)}</td>
                    <td>{item.is_active ? "active" : "removed"}</td>
                    <td>
                      <button
                        className="ghost-button maker-delete-button"
                        type="button"
                        disabled={!item.is_active || activeAction === `product-${item.id}`}
                        onClick={() => handleRemoveProduct(item.id)}
                      >
                        {activeAction === `product-${item.id}` ? "Removing..." : "Remove"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="admin-section">
          <div className="admin-section-heading">
            <div>
              <p className="eyebrow">Verifications</p>
              <h2>Maker shop verification</h2>
            </div>
          </div>
          <div className="admin-table-wrap">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Maker</th>
                  <th>Shop</th>
                  <th>Profile status</th>
                  <th>Decision</th>
                  <th>Notes</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {verifications.map((item) => (
                  <tr key={item.maker_id}>
                    <td>
                      <strong>{item.maker_name}</strong>
                      <div className="admin-cell-muted">{item.contact_email || "No contact email"}</div>
                    </td>
                    <td>{item.shop_name || "No shop profile yet"}</td>
                    <td>{item.profile_verification_status}</td>
                    <td>
                      <select
                        className="form-input admin-select"
                        value={verificationDrafts[item.maker_id]?.status || item.status}
                        onChange={(event) =>
                          handleVerificationChange(item.maker_id, "status", event.target.value)
                        }
                        disabled={activeAction === `verification-${item.maker_id}`}
                      >
                        <option value="pending">pending</option>
                        <option value="verified">verified</option>
                        <option value="rejected">rejected</option>
                      </select>
                    </td>
                    <td>
                      <textarea
                        className="form-input admin-notes-input"
                        rows={2}
                        value={verificationDrafts[item.maker_id]?.notes || ""}
                        onChange={(event) =>
                          handleVerificationChange(item.maker_id, "notes", event.target.value)
                        }
                        disabled={activeAction === `verification-${item.maker_id}`}
                        placeholder="Admin notes"
                      />
                    </td>
                    <td>
                      <button
                        className="form-submit"
                        type="button"
                        disabled={activeAction === `verification-${item.maker_id}`}
                        onClick={() => handleVerificationSave(item.maker_id)}
                      >
                        {activeAction === `verification-${item.maker_id}` ? "Saving..." : "Save"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="admin-section">
          <div className="admin-section-heading">
            <div>
              <p className="eyebrow">Reviews</p>
              <h2>Moderate reviews</h2>
            </div>
          </div>
          <div className="admin-table-wrap">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Customer</th>
                  <th>Target</th>
                  <th>Rating</th>
                  <th>Comment</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {reviews.map((item) => (
                  <tr key={item.id}>
                    <td>{item.id}</td>
                    <td>{item.customer_name}</td>
                    <td>
                      <strong>{item.target_name}</strong>
                      <div className="admin-cell-muted">{item.target_type}</div>
                    </td>
                    <td>{item.rating} / 5</td>
                    <td>{item.comment || "No comment"}</td>
                    <td>
                      <button
                        className="ghost-button maker-delete-button"
                        type="button"
                        disabled={activeAction === `review-${item.id}`}
                        onClick={() => handleRemoveReview(item.id)}
                      >
                        {activeAction === `review-${item.id}` ? "Removing..." : "Remove"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </section>
    </AppShell>
  );
}
