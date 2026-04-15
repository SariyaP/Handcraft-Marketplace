import { getApiUrl, parseApiResponse } from "./auth";

export async function createCommission(token, payload) {
  const response = await fetch(getApiUrl("/commissions"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  return parseApiResponse(response);
}

export async function fetchCustomerCommissions(token) {
  const response = await fetch(getApiUrl("/commissions"), {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    cache: "no-store",
  });

  return parseApiResponse(response);
}

export async function fetchMakerCommissions(token) {
  const response = await fetch(getApiUrl("/maker/commissions"), {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    cache: "no-store",
  });

  return parseApiResponse(response);
}

export async function updateCommissionStatus(commissionId, token, status) {
  const response = await fetch(getApiUrl(`/commissions/${commissionId}`), {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ status }),
  });

  return parseApiResponse(response);
}

export async function createCommissionWipUpdate(commissionId, token, payload) {
  const response = await fetch(getApiUrl(`/commissions/${commissionId}/updates`), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  return parseApiResponse(response);
}
