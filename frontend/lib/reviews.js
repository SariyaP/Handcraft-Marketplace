import { getApiUrl, parseApiResponse } from "./auth";

export async function createProductReview(productId, token, payload) {
  const response = await fetch(getApiUrl(`/products/${productId}/reviews`), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  return parseApiResponse(response);
}

export async function createCommissionReview(commissionId, token, payload) {
  const response = await fetch(getApiUrl(`/commissions/${commissionId}/reviews`), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  return parseApiResponse(response);
}

export async function fetchMakerReviews(token) {
  const response = await fetch(getApiUrl("/maker/reviews"), {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    cache: "no-store",
  });

  return parseApiResponse(response);
}
