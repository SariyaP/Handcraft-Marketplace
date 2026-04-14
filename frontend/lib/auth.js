export const TOKEN_KEY = "handcraft_marketplace_token";
export const USER_KEY = "handcraft_marketplace_user";

const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export function getApiUrl(path) {
  return `${apiBaseUrl}${path}`;
}

export function getRedirectPathForRole(role) {
  switch (role) {
    case "customer":
      return "/customer";
    case "maker":
      return "/maker";
    case "admin":
      return "/admin";
    default:
      return "/home";
  }
}

export function persistAuthSession(payload) {
  if (typeof window === "undefined") {
    return;
  }

  localStorage.setItem(TOKEN_KEY, payload.access_token);
  localStorage.setItem(USER_KEY, JSON.stringify(payload.user));
}

export function clearAuthSession() {
  if (typeof window === "undefined") {
    return;
  }

  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function getStoredToken() {
  if (typeof window === "undefined") {
    return null;
  }

  return localStorage.getItem(TOKEN_KEY);
}

export function getStoredUser() {
  if (typeof window === "undefined") {
    return null;
  }

  const rawUser = localStorage.getItem(USER_KEY);
  if (!rawUser) {
    return null;
  }

  try {
    return JSON.parse(rawUser);
  } catch {
    clearAuthSession();
    return null;
  }
}

export async function parseApiResponse(response) {
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const message =
      data?.detail ||
      data?.message ||
      "Something went wrong while contacting the server.";
    throw new Error(message);
  }

  return data;
}

export async function loginUser(values) {
  const response = await fetch(getApiUrl("/auth/login"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(values),
  });

  return parseApiResponse(response);
}

export async function registerUser(values) {
  const response = await fetch(getApiUrl("/auth/register"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(values),
  });

  return parseApiResponse(response);
}

export async function fetchCurrentUser(token) {
  const response = await fetch(getApiUrl("/auth/me"), {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    cache: "no-store",
  });

  return parseApiResponse(response);
}
