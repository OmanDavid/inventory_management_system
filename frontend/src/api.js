const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(path, options = {}) {
  let res;
  try {
    res = await fetch(`${BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch (err) {
    throw new ApiError(
      "Can't reach the API. Is the Flask server running on " + BASE_URL + "?",
      0
    );
  }

  let body = null;
  try {
    body = await res.json();
  } catch {
    // no body
  }

  if (!res.ok) {
    throw new ApiError(body?.error || `Request failed (${res.status})`, res.status);
  }
  return body;
}

export const api = {
  health: () => request("/health"),

  listItems: () => request("/inventory"),
  getItem: (id) => request(`/inventory/${id}`),
  createItem: (data) =>
    request("/inventory", { method: "POST", body: JSON.stringify(data) }),
  updateItem: (id, data) =>
    request(`/inventory/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteItem: (id) => request(`/inventory/${id}`, { method: "DELETE" }),

  lookupExternal: ({ barcode, name }) => {
    const params = new URLSearchParams();
    if (barcode) params.set("barcode", barcode);
    if (name) params.set("name", name);
    return request(`/inventory/lookup?${params.toString()}`);
  },
  importExternal: (data) =>
    request("/inventory/import", { method: "POST", body: JSON.stringify(data) }),
};

export { ApiError };
