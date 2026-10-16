import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

const COLORS = ["#4f46e5", "#06b6d4", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6",
                "#ec4899", "#14b8a6", "#84cc16", "#f97316", "#64748b", "#0ea5e9"];

// nameKey is "category" or "source" - the field name returned by the API.
export default function DonutChart({ data, nameKey }) {
  if (!data.length) return <p className="muted">No data yet.</p>;
  return (
    <div className="chart-box">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={data} dataKey="count" nameKey={nameKey} innerRadius="45%" outerRadius="72%"
               paddingAngle={2}>
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend verticalAlign="bottom" wrapperStyle={{ fontSize: 12 }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
