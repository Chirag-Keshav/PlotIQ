import { useNavigate } from "react-router-dom";
import { MapPin, ArrowRight } from "lucide-react";
import { motion } from "motion/react";

interface RiskFlag {
  type: string;
  severity: "high" | "medium" | "low";
}

interface ListingCardProps {
  listing: {
    id: string;
    title: string;
    locality: string;
    price_lakhs: number;
    area_sqyd: number;
    confidence_score: number | null;
    risk_flags: RiskFlag[];
    listing_status: string;
    lat: number;
    lng: number;
  };
}

function ConfidenceScoreBadge({ score }: { score: number | null }) {
  if (score === null)
    return (
      <span className="px-2 py-0.5 rounded text-xs font-bold bg-white/5 text-white/40 border border-white/10">
        Unscored
      </span>
    );
  if (score >= 80)
    return (
      <span className="px-2 py-0.5 rounded text-xs font-bold bg-green-500/20 text-green-400 border border-green-500/30">
        {score}
      </span>
    );
  if (score >= 50)
    return (
      <span className="px-2 py-0.5 rounded text-xs font-bold bg-yellow-500/20 text-yellow-400 border border-yellow-500/30">
        {score}
      </span>
    );
  return (
    <span className="px-2 py-0.5 rounded text-xs font-bold bg-red-500/20 text-red-400 border border-red-500/30">
      {score}
    </span>
  );
}

function RiskFlagPill({ flag }: { flag: RiskFlag }) {
  const colors = {
    high: "bg-red-500/10 text-red-400 border-red-500/20",
    medium: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
    low: "bg-white/5 text-white/50 border-white/10",
  };
  return (
    <span
      className={`px-2 py-0.5 rounded text-xs font-medium border ${colors[flag.severity]}`}
    >
      {flag.type.replace(/_/g, " ")}
    </span>
  );
}

export default function ListingCard({ listing }: ListingCardProps) {
  const navigate = useNavigate();

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-4 cursor-pointer hover:bg-white/5 transition-colors"
      onClick={() => navigate(`/listings/${listing.id}`)}
    >
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold text-white text-sm leading-tight flex-1 pr-2 truncate">
          {listing.title}
        </h3>
        <ConfidenceScoreBadge score={listing.confidence_score} />
      </div>

      <div className="flex items-center gap-1 text-white/50 text-xs mb-3">
        <MapPin className="h-3 w-3" />
        <span>{listing.locality}</span>
        <span className="mx-1">·</span>
        <span>{listing.area_sqyd} sqyd</span>
      </div>

      <div className="flex justify-between items-center">
        <span className="text-xl font-bold font-mono text-white">
          ₹{listing.price_lakhs}L
        </span>
        <div className="flex items-center gap-1">
          {listing.risk_flags.slice(0, 2).map((f, i) => (
            <RiskFlagPill key={i} flag={f} />
          ))}
        </div>
      </div>

      <button
        className="mt-3 w-full flex items-center justify-center gap-2 py-2 bg-white/5 border border-white/10 rounded-lg text-xs font-semibold text-white/70 hover:bg-white/10 hover:text-white transition-colors"
        onClick={(e) => {
          e.stopPropagation();
          navigate(`/listings/${listing.id}`);
        }}
      >
        Analyze <ArrowRight className="h-3 w-3" />
      </button>
    </motion.div>
  );
}
