const CARDS = [
  { key: "total_listings", label: "Total Listings", icon: "🏢" },
  { key: "total_cities", label: "Cities", icon: "🌆" },
  { key: "total_categories", label: "Categories", icon: "🗂️" },
  { key: "total_sources", label: "Sources", icon: "🔗" },
];

export default function KpiCards({ summary, loading }) {
  return (
    <section className="kpi-grid">
      {CARDS.map((card) => (
        <div className="card kpi" key={card.key}>
          <span className="kpi-icon">{card.icon}</span>
          <div>
            <div className="kpi-label">{card.label}</div>
            <div className="kpi-value">
              {loading && !summary ? "…" : (summary?.[card.key] ?? 0).toLocaleString("en-IN")}
            </div>
          </div>
        </div>
      ))}
    </section>
  );
}
