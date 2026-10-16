// All backend calls live here. Field names match the FastAPI responses exactly.
const BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

async function request(path, params = {}) {
  const url = new URL(BASE_URL + path);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") url.searchParams.set(key, value);
  });

  let response;
  try {
    response = await fetch(url);
  } catch {
    throw new Error(`Cannot reach the API at ${BASE_URL}. Is the backend running?`);
  }

  if (!response.ok) {
    let message = `Request failed (HTTP ${response.status})`;
    try {
      const body = await response.json();
      if (typeof body.detail === "string") message = body.detail;
      else if (Array.isArray(body.detail)) message = body.detail.map((d) => d.msg).join("; ");
    } catch {
      /* response was not JSON, keep default message */
    }
    throw new Error(message);
  }
  return response.json();
}

// -> { total_listings, total_cities, total_categories, total_sources }
export const getSummary = () => request("/api/dashboard/summary");
// -> [{ city, count }]
export const getCityWise = () => request("/api/dashboard/city-wise");
// -> [{ category, count }]
export const getCategoryWise = () => request("/api/dashboard/category-wise");
// -> [{ source, count }]
export const getSourceWise = () => request("/api/dashboard/source-wise");
// -> { items: [{ id, business_name, category, city, address, phone, source, created_at }], total, page, page_size }
export const getListings = (params) => request("/api/listings", params);
