import DisclaimerBanner from "../../ui/DisclaimerBanner";
import { TrendingUp, ExternalLink } from "lucide-react";

interface GrowthSignal {
  id: string;
  signal_type: string;
  title: string;
  source_url?: string;
  source_type?: string;
  status: string;
  announced_date?: string;
  confidence?: number;
}

interface FutureGrowthTabProps {
  growthTier: string | null;
  signals: GrowthSignal[];
  isLoading: boolean;
}

const STATUS_COLORS: Record<string, string> = {
  operational: "bg-green-500/20 text-green-400 border-green-500/30",
  under_construction: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  approved: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
  announced: "bg-white/10 text-white/50 border-white/20",
};

const TIER_STYLES: Record<string, { bg: string; text: string; desc: string }> = {
  "High Growth Corridor": {
    bg: "bg-green-500/20 border-green-500/30",
    text: "text-green-400",
    desc: "3+ approved or active infrastructure projects within 10km",
  },
  "Emerging Zone": {
    bg: "bg-yellow-500/20 border-yellow-500/30",
    text: "text-yellow-400",
    desc: "1–2 approved or active infrastructure projects within 10km",
  },
  Speculative: {
    bg: "bg-white/5 border-white/10",
    text: "text-white/50",
    desc: "Only announced projects or no signals nearby",
  },
};

export default function FutureGrowthTab({ growthTier, signals, isLoading }: FutureGrowthTabProps) {
  const tierStyle = growthTier ? TIER_STYLES[growthTier] ?? TIER_STYLES["Speculative"] : null;

  return (
    <div className="space-y-6">
      <DisclaimerBanner variant="growth" />

      {/* Growth tier badge */}
      {tierStyle && growthTier && (
        <div className={`p-4 border rounded-xl ${tierStyle.bg}`}>
          <div className="flex items-center gap-2 mb-1">
            <TrendingUp className={`h-5 w-5 ${tierStyle.text}`} />
            <span className={`font-bold text-lg ${tierStyle.text}`}>{growthTier}</span>
          </div>
          <p className="text-xs text-white/40">{tierStyle.desc}</p>
        </div>
      )}

      {/* Signals list */}
      {isLoading ? (
        <div className="text-center py-8 text-white/30 text-sm">Loading growth signals...</div>
      ) : signals.length === 0 ? (
        <div className="text-center py-8 text-white/30 text-sm">
          No growth signals found within 10km of this listing.
        </div>
      ) : (
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider">
            Nearby Infrastructure Projects
          </h3>
          {signals.map((s) => {
            const statusClass = STATUS_COLORS[s.status] ?? STATUS_COLORS["announced"];
            return (
              <div key={s.id} className="p-4 bg-white/3 border border-white/10 rounded-xl space-y-2">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <p className="text-sm font-semibold text-white flex-1">{s.title}</p>
                  <span className={`px-2 py-0.5 rounded-full text-xs font-bold border ${statusClass}`}>
                    {s.status.replace(/_/g, " ")}
                  </span>
                </div>
                <div className="flex flex-wrap gap-3 text-xs text-white/40">
                  <span>{s.signal_type.replace(/_/g, " ")}</span>
                  {s.source_type && <span>· {s.source_type}</span>}
                  {s.announced_date && <span>· Announced {s.announced_date}</span>}
                  {s.confidence && <span>· {(s.confidence * 100).toFixed(0)}% confidence</span>}
                </div>
                {s.source_url && (
                  <a
                    href={s.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-xs text-white/40 hover:text-white transition-colors"
                  >
                    Source <ExternalLink className="h-3 w-3" />
                  </a>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
