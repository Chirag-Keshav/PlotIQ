import { RadialBarChart, RadialBar, ResponsiveContainer } from "recharts";
import DisclaimerBanner from "../../ui/DisclaimerBanner";

interface ScoreBreakdown {
  document_completeness: number;
  owner_kyc: number;
  geo_consistency: number;
  duplicate_detection: number;
  pricing_anomaly: number;
  listing_freshness: number;
  aggregate: number;
}

interface AIScoreTabProps {
  score: number | null;
  breakdown: ScoreBreakdown | null;
}

const DIMENSIONS = [
  { key: "document_completeness", label: "Document Completeness", weight: "25%" },
  { key: "owner_kyc", label: "Owner KYC", weight: "20%" },
  { key: "geo_consistency", label: "Geo Consistency", weight: "15%" },
  { key: "duplicate_detection", label: "Duplicate Detection", weight: "20%" },
  { key: "pricing_anomaly", label: "Pricing Anomaly Check", weight: "10%" },
  { key: "listing_freshness", label: "Listing Freshness", weight: "10%" },
] as const;

function scoreColor(score: number): string {
  if (score >= 80) return "#4ade80";
  if (score >= 50) return "#facc15";
  return "#f87171";
}

export default function AIScoreTab({ score, breakdown }: AIScoreTabProps) {
  if (score === null || !breakdown) {
    return (
      <div className="space-y-4">
        <DisclaimerBanner variant="score" />
        <div className="text-center py-12 text-white/40">
          <p>Score computation in progress...</p>
          <p className="text-sm mt-1">This may take up to 30 seconds after listing creation.</p>
        </div>
      </div>
    );
  }

  const chartData = [{ value: score, fill: scoreColor(score) }];

  return (
    <div className="space-y-6">
      <DisclaimerBanner variant="score" />

      {/* Radial chart */}
      <div className="flex flex-col items-center">
        <div className="relative w-48 h-48">
          <ResponsiveContainer width="100%" height="100%">
            <RadialBarChart
              innerRadius="60%"
              outerRadius="90%"
              data={chartData}
              startAngle={90}
              endAngle={90 - (score / 100) * 360}
            >
              <RadialBar dataKey="value" background={{ fill: "#ffffff10" }} />
            </RadialBarChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-4xl font-bold font-mono" style={{ color: scoreColor(score) }}>
              {score}
            </span>
            <span className="text-xs text-white/40">/ 100</span>
          </div>
        </div>
      </div>

      {/* Per-dimension breakdown */}
      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider">Score Breakdown</h3>
        {DIMENSIONS.map(({ key, label, weight }) => {
          const dimScore = breakdown[key];
          return (
            <div key={key} className="p-3 bg-white/3 border border-white/10 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-white font-medium">{label}</span>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-white/30">{weight}</span>
                  <span className="text-sm font-bold font-mono" style={{ color: scoreColor(dimScore) }}>
                    {dimScore}
                  </span>
                </div>
              </div>
              <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{ width: `${dimScore}%`, backgroundColor: scoreColor(dimScore) }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
