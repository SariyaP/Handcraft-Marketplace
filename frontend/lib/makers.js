import { getApiUrl, parseApiResponse } from "./auth";

export async function fetchOwnMakerProfile(token) {
  const response = await fetch(getApiUrl("/maker/profile"), {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    cache: "no-store",
  });

  return parseApiResponse(response);
}

export async function updateOwnMakerProfile(token, payload) {
  const response = await fetch(getApiUrl("/maker/profile"), {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  return parseApiResponse(response);
}

export async function fetchPublicMakerProfile(makerId) {
  const response = await fetch(getApiUrl(`/makers/${makerId}`), {
    method: "GET",
    cache: "no-store",
  });

  return parseApiResponse(response);
}
