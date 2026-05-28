import { BadgeCheck, Clock, MapPin, User } from "lucide-react";

interface OverviewTabProps {
  listing: {
    title: string;
    description?: string;
    locality: string;
    lat: number;
    lng: number;
    area_sqyd: number;
    price_lakhs: number;
    use_type?: string;
    road_access?: string;
    ownership_type?: string;
    verification_tier: string;
    created_at?: string;
  };
}

export default function OverviewTab({ listing }: OverviewTabProps) {
  const listingAgeDays = listing.created_at
    ? Math.floor((Date.now() - new Date(listing.created_at).getTime()) / 86_400_000)
    : null;

  const mapUrl = `https://maps.googleapis.com/maps/api/staticmap?center=${listing.lat},${listing.lng}&zoom=14&size=600x300&markers=color:red%7C${listing.lat},${listing.lng}&key=${import.meta.env.VITE_GOOGLE_MAPS_API_KEY ?? ""}`;

  return (
    <div className="space-y-6">
      {/* Thumbnail map */}
      <div className="rounded-xl overflow-hidden border border-white/10 h-48 bg-white/5 flex items-center justify-center">
        {import.meta.env.VITE_GOOGLE_MAPS_API_KEY ? (
          <img src={mapUrl} alt="Plot location" className="w-full h-full object-cover" />
        ) : (
          <div className="text-white/30 text-sm flex flex-col items-center gap-2">
            <MapPin className="h-6 w-6" />
            <span>Map thumbnail (requires VITE_GOOGLE_MAPS_API_KEY)</span>
            <span className="text-xs">{listing.lat.toFixed(4)}, {listing.lng.toFixed(4)}</span>
          </div>
        )}
      </div>

      {/* Description */}
      {listing.description && (
        <p className="text-white/70 text-sm leading-relaxed">{listing.description}</p>
      )}

      {/* Details grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {[
          { label: "Use Type", value: listing.use_type ?? "—" },
          { label: "Road Access", value: listing.road_access ?? "—" },
          { label: "Ownership", value: listing.ownership_type ?? "—" },
          { label: "Area", value: `${listing.area_sqyd} sqyd` },
          { label: "Price/sqyd", value: `₹${((listing.price_lakhs * 100000) / Number(listing.area_sqyd)).toFixed(0)}` },
          { label: "Locality", value: listing.locality },
        ].map(({ label, value }) => (
          <div key={label} className="p-3 bg-white/3 border border-white/10 rounded-lg">
            <p className="text-xs text-white/40 uppercase tracking-wider mb-1">{label}</p>
            <p className="text-sm font-medium text-white capitalize">{value}</p>
          </div>
        ))}
      </div>

      {/* Owner info */}
      <div className="p-4 bg-white/3 border border-white/10 rounded-xl flex items-center gap-3">
        <div className="h-10 w-10 rounded-full bg-white/10 flex items-center justify-center">
          <User className="h-5 w-5 text-white/60" />
        </div>
        <div className="flex-1">
          <p className="text-sm font-medium text-white">Owner</p>
          <p className="text-xs text-white/40">
            {listing.ownership_type ?? "Individual"} owner
          </p>
        </div>
        {listing.verification_tier === "full" ? (
          <span className="flex items-center gap-1 text-xs text-green-400 font-medium">
            <BadgeCheck className="h-4 w-4" /> Verified
          </span>
        ) : (
          <span className="flex items-center gap-1 text-xs text-white/40 font-medium">
            <Clock className="h-4 w-4" /> Unverified
          </span>
        )}
      </div>

      {listingAgeDays !== null && (
        <p className="text-xs text-white/30">Listed {listingAgeDays} day{listingAgeDays !== 1 ? "s" : ""} ago</p>
      )}
    </div>
  );
}
