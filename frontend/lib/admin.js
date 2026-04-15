import { getApiUrl, parseApiResponse } from "./auth";

async function authenticatedAdminRequest(path, token, options = {}) {
  const response = await fetch(getApiUrl(path), {
    ...options,
    headers: {
      ...(options.headers || {}),
      Authorization: `Bearer ${token}`,
    },
    cache: options.cache || "no-store",
  });

  if (!response.ok) {
    return parseApiResponse(response);
  }

  if (response.status === 204) {
    return null;
  }

  return parseApiResponse(response);
}

export function fetchAdminUsers(token) {
  return authenticatedAdminRequest("/admin/users", token);
}

export function updateAdminUser(userId, token, payload) {
  return authenticatedAdminRequest(`/admin/users/${userId}`, token, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export function fetchAdminProducts(token) {
  return authenticatedAdminRequest("/admin/products", token);
}

export function removeAdminProduct(productId, token) {
  return authenticatedAdminRequest(`/admin/products/${productId}`, token, {
    method: "DELETE",
  });
}

export function fetchAdminVerifications(token) {
  return authenticatedAdminRequest("/admin/verifications", token);
}

export function updateAdminVerification(makerId, token, payload) {
  return authenticatedAdminRequest(`/admin/verifications/${makerId}`, token, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export function fetchAdminReviews(token) {
  return authenticatedAdminRequest("/admin/reviews", token);
}

export function removeAdminReview(reviewId, token) {
  return authenticatedAdminRequest(`/admin/reviews/${reviewId}`, token, {
    method: "DELETE",
  });
}
