import { useEffect, useState } from "react";
import { getCategoryWise, getCityWise, getSourceWise, getSummary } from "./api";
import KpiCards from "./components/KpiCards.jsx";
import CityBarChart from "./components/CityBarChart.jsx";
import DonutChart from "./components/DonutChart.jsx";
import ListingsTable from "./components/ListingsTable.jsx";

export default function App() {
  const [summary, setSummary] = useState(null);
  const [cities, setCities] = useState([]);
  const [categories, setCategories] = useState([]);
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshKey, setRefreshKey] = useState(0); // bump this number to reload everything

  useEffect(() => {
    let ignore = false;
    setLoading(true);
    setError("");
    Promise.all([getSummary(), getCityWise(), getCategoryWise(), getSourceWise()])
      .then(([s, c, cat, src]) => {
        if (ignore) return;
        setSummary(s);
        setCities(c);
        setCategories(cat);
        setSources(src);
      })
      .catch((e) => !ignore && setError(e.message))
      .finally(() => !ignore && setLoading(false));
    return () => {
      ignore = true;
    };
  }, [refreshKey]);

  return (
    <div className="page">
      <header className="header">
        <div>
          <h1>Business Listings Dashboard</h1>
          <p className="muted">Demo data is synthetic (computer-generated), not real businesses.</p>
        </div>
        <button className="primary" onClick={() => setRefreshKey((k) => k + 1)} disabled={loading}>
          {loading ? "Refreshing…" : "⟳ Refresh"}
        </button>
      </header>

      {error && (
        <div className="error">
          ⚠️ {error}
          <button onClick={() => setRefreshKey((k) => k + 1)}>Try again</button>
        </div>
      )}

      <KpiCards summary={summary} loading={loading} />

      <section className="chart-grid">
        <div className="card wide">
          <h2>Listings by City</h2>
          <CityBarChart data={cities} />
        </div>
        <div className="card">
          <h2>Listings by Category</h2>
          <DonutChart data={categories} nameKey="category" />
        </div>
        <div className="card">
          <h2>Listings by Source</h2>
          <DonutChart data={sources} nameKey="source" />
        </div>
      </section>

      <ListingsTable refreshKey={refreshKey} />
    </div>
  );
}
