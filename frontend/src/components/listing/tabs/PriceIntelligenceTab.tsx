import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import DisclaimerBanner from "../../ui/DisclaimerBanner";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface PriceEstimate {
  estimate: { p10_lakhs: number; p50_lakhs: number; p90_lakhs: number };
  classification: "overpriced" | "underpriced" | "fair";
  negotiation_range: { low_lakhs: number; high_lakhs: number };
  comparables: Array<{
    locality: string;
    area_sqyd: number;
    price_lakhs: number;
    price_per_sqyd: number;
    distance_km: number;
  }>;
  price_trend: Array<{ month: string; median_price_per_sqyd: number }>;
}

interface PriceIntelligenceTabProps {
  data: PriceEstimate | null;
  isLoading: boolean;
}

function ClassificationBadge({ cls }: { cls: string }) {
  if (cls === "overpriced")
    return (
      <span className="flex items-center gap-1 px-3 py-1 bg-red-500/20 text-red-400 border border-red-500/30 rounded-full text-sm font-bold">
        <TrendingUp className="h-4 w-4" /> Overpriced
      </span>
    );
  if (cls === "underpriced")
    return (
      <span className="flex items-center gap-1 px-3 py-1 bg-green-500/20 text-green-400 border border-green-500/30 rounded-full text-sm font-bold">
        <TrendingDown className="h-4 w-4" /> Underpriced
      </span>
    );
  return (
    <span className="flex items-center gap-1 px-3 py-1 bg-white/10 text-white/70 border border-white/20 rounded-full text-sm font-bold">
      <Minus className="h-4 w-4" /> Fair Price
    </span>
  );
}

export default function PriceIntelligenceTab({ data, isLoading }: PriceIntelligenceTabProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        <DisclaimerBanner variant="price" />
        <div className="text-center py-12 text-white/40 text-sm">Loading price intelligence...</div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="space-y-4">
        <DisclaimerBanner variant="price" />
        <div className="text-center py-12 text-white/40 text-sm">Price estimate not available.</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <DisclaimerBanner variant="price" />

      {/* Price range + classification */}
      <div className="p-4 bg-white/3 border border-white/10 rounded-xl">
        <div className="flex flex-wrap justify-between items-start gap-4 mb-4">
          <div>
            <p className="text-xs text-white/40 uppercase tracking-wider mb-1">Estimated Fair Value</p>
            <p className="text-2xl font-bold font-mono text-white">
              ₹{data.estimate.p50_lakhs.toFixed(1)}L
            </p>
            <p className="text-xs text-white/40 mt-1">
              Range ₹{data.estimate.p10_lakhs.toFixed(1)}L – ₹{data.estimate.p90_lakhs.toFixed(1)}L
            </p>
          </div>
          <ClassificationBadge cls={data.classification} />
        </div>

        <div className="p-3 bg-white/3 border border-white/10 rounded-lg">
          <p className="text-xs text-white/40 mb-1">Negotiation Range</p>
          <p className="text-sm font-semibold text-white">
            ₹{data.negotiation_range.low_lakhs.toFixed(1)}L – ₹{data.negotiation_range.high_lakhs.toFixed(1)}L
          </p>
        </div>
      </div>

      {/* Price trend chart */}
      {data.price_trend.length > 0 && (
        <div className="p-4 bg-white/3 border border-white/10 rounded-xl">
          <h3 className="text-sm font-semibold text-white mb-4">Price Trend (₹/sqyd)</h3>
          <ResponsiveContainer width="100%" height={160}>
            <LineChart data={data.price_trend}>
              <XAxis dataKey="month" tick={{ fill: "#ffffff40", fontSize: 10 }} />
              <YAxis tick={{ fill: "#ffffff40", fontSize: 10 }} />
              <Tooltip
                contentStyle={{ background: "#0a0a0a", border: "1px solid #ffffff20", color: "#fff", fontSize: 12 }}
              />
              <Line
                type="monotone"
                dataKey="median_price_per_sqyd"
                stroke="#ffffff"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Comparables */}
      {data.comparables.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider mb-3">
            Comparable Plots
          </h3>
          <div className="space-y-2">
            {data.comparables.map((c, i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-white/3 border border-white/10 rounded-lg">
                <div>
                  <p className="text-sm text-white">{c.locality}</p>
                  <p className="text-xs text-white/40">{c.area_sqyd} sqyd · {c.distance_km.toFixed(1)} km away</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-bold font-mono text-white">₹{c.price_lakhs}L</p>
                  <p className="text-xs text-white/40">₹{c.price_per_sqyd.toFixed(0)}/sqyd</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
