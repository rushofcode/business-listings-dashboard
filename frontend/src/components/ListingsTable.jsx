import { useEffect, useState } from "react";
import { getListings } from "../api";

const PAGE_SIZE = 10;

export default function ListingsTable({ refreshKey }) {
  const [searchInput, setSearchInput] = useState("");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [result, setResult] = useState({ items: [], total: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Wait 400 ms after typing stops, so we don't call the API on every key press.
  useEffect(() => {
    const timer = setTimeout(() => {
      setSearch(searchInput.trim());
      setPage(1);
    }, 400);
    return () => clearTimeout(timer);
  }, [searchInput]);

  useEffect(() => {
    let ignore = false;
    setLoading(true);
    setError("");
    getListings({ search, page, page_size: PAGE_SIZE })
      .then((data) => !ignore && setResult(data))
      .catch((e) => !ignore && setError(e.message))
      .finally(() => !ignore && setLoading(false));
    return () => {
      ignore = true;
    };
  }, [search, page, refreshKey]);

  const totalPages = Math.max(1, Math.ceil(result.total / PAGE_SIZE));

  return (
    <section className="card">
      <div className="table-head">
        <h2>Listings</h2>
        <input
          className="search"
          type="search"
          placeholder="Search name, category, city, phone, source…"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
        />
      </div>

      {error && <div className="error">⚠️ {error}</div>}

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th><th>Business Name</th><th>Category</th><th>City</th>
              <th>Address</th><th>Phone</th><th>Source</th><th>Created</th>
            </tr>
          </thead>
          <tbody>
            {result.items.map((row) => (
              <tr key={row.id}>
                <td>{row.id}</td>
                <td><strong>{row.business_name}</strong></td>
                <td>{row.category}</td>
                <td>{row.city}</td>
                <td>{row.address}</td>
                <td>{row.phone}</td>
                <td>{row.source}</td>
                <td>{new Date(row.created_at).toLocaleDateString("en-IN")}</td>
              </tr>
            ))}
            {!loading && !error && result.items.length === 0 && (
              <tr><td colSpan="8" className="muted center">No listings found.</td></tr>
            )}
            {loading && (
              <tr><td colSpan="8" className="muted center">Loading…</td></tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="pager">
        <span className="muted">{result.total.toLocaleString("en-IN")} results</span>
        <div>
          <button onClick={() => setPage((p) => p - 1)} disabled={page <= 1 || loading}>← Prev</button>
          <span className="page-info">Page {page} of {totalPages}</span>
          <button onClick={() => setPage((p) => p + 1)} disabled={page >= totalPages || loading}>Next →</button>
        </div>
      </div>
    </section>
  );
}
