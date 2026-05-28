import { BadgeCheck, AlertCircle, Clock } from "lucide-react";

interface ListingHeaderProps {
  title: string;
  locality: string;
  price_lakhs: number;
  area_sqyd: number;
  verification_tier: string;
  listing_status: string;
  created_at?: string;
}

function VerificationBadge({ tier }: { tier: string }) {
  if (tier === "full")
    return (
      <span className="flex items-center gap-1 px-3 py-1 bg-green-500/20 text-green-400 border border-green-500/30 rounded-full text-xs font-bold">
        <BadgeCheck className="h-3 w-3" /> Fully Verified
      </span>
    );
  if (tier === "partial")
    return (
      <span className="flex items-center gap-1 px-3 py-1 bg-yellow-500/20 text-yellow-400 border border-yellow-500/30 rounded-full text-xs font-bold">
        <AlertCircle className="h-3 w-3" /> Partial Verification
      </span>
    );
  return (
    <span className="flex items-center gap-1 px-3 py-1 bg-white/5 text-white/40 border border-white/10 rounded-full text-xs font-bold">
      <Clock className="h-3 w-3" /> Unverified
    </span>
  );
}

export default function ListingHeader({
  title,
  locality,
  price_lakhs,
  area_sqyd,
  verification_tier,
  created_at,
}: ListingHeaderProps) {
  const listingAgeDays = created_at
    ? Math.floor((Date.now() - new Date(created_at).getTime()) / 86_400_000)
    : null;

  return (
    <div className="mb-8">
      <div className="flex flex-wrap items-start justify-between gap-4 mb-3">
        <h1 className="text-3xl md:text-4xl font-bold text-white leading-tight flex-1">
          {title}
        </h1>
        <VerificationBadge tier={verification_tier} />
      </div>
      <p className="text-white/60 text-lg mb-4">
        {locality} &middot; {area_sqyd} sqyd
      </p>
      <div className="flex flex-wrap items-center gap-4">
        <span className="text-3xl font-mono font-bold text-white">
          ₹{price_lakhs}L
        </span>
        <span className="text-white/40 text-sm">
          ₹{((price_lakhs * 100000) / Number(area_sqyd)).toFixed(0)}/sqyd
        </span>
        {listingAgeDays !== null && (
          <span className="text-white/40 text-sm">
            Listed {listingAgeDays}d ago
          </span>
        )}
      </div>
    </div>
  );
}
