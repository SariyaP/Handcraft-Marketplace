import { getApiUrl, parseApiResponse } from "./auth";

export async function fetchProducts(filters = {}) {
  const searchParams = new URLSearchParams();

  if (filters.minPrice) {
    searchParams.set("min_price", filters.minPrice);
  }

  if (filters.maxPrice) {
    searchParams.set("max_price", filters.maxPrice);
  }

  if (filters.makerId) {
    searchParams.set("maker_id", filters.makerId);
  }

  const queryString = searchParams.toString();
  const url = queryString
    ? getApiUrl(`/products?${queryString}`)
    : getApiUrl("/products");

  const response = await fetch(url, {
    method: "GET",
    cache: "no-store",
  });

  return parseApiResponse(response);
}

export async function fetchProduct(productId) {
  const response = await fetch(getApiUrl(`/products/${productId}`), {
    method: "GET",
    cache: "no-store",
  });

  return parseApiResponse(response);
}

export async function fetchCustomerDashboard(token) {
  const response = await fetch(getApiUrl("/dashboard/customer/overview"), {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    cache: "no-store",
  });

  return parseApiResponse(response);
}

export async function createProductOrder(productId, token, payload) {
  const response = await fetch(getApiUrl(`/products/${productId}/orders`), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  return parseApiResponse(response);
}

export async function fetchMakerProducts(token) {
  const response = await fetch(getApiUrl("/maker/products"), {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    cache: "no-store",
  });

  return parseApiResponse(response);
}

export async function createMakerProduct(token, payload) {
  const response = await fetch(getApiUrl("/products"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  return parseApiResponse(response);
}

export async function updateMakerProduct(productId, token, payload) {
  const response = await fetch(getApiUrl(`/products/${productId}`), {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  return parseApiResponse(response);
}

export async function deleteMakerProduct(productId, token) {
  const response = await fetch(getApiUrl(`/products/${productId}`), {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    return parseApiResponse(response);
  }
}

export async function fetchWishlist(token) {
  const response = await fetch(getApiUrl("/wishlist"), {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    cache: "no-store",
  });

  return parseApiResponse(response);
}

export async function addWishlistItem(productId, token) {
  const response = await fetch(getApiUrl("/wishlist"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ product_id: productId }),
  });

  return parseApiResponse(response);
}

export async function removeWishlistItem(productId, token) {
  const response = await fetch(getApiUrl(`/wishlist/${productId}`), {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    return parseApiResponse(response);
  }
}
