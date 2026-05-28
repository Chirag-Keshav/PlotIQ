import { useState } from "react";
import { School, Building2, ShoppingBag, Train, Route, Bus } from "lucide-react";
import DisclaimerBanner from "../../ui/DisclaimerBanner";

interface POI {
  name: string;
  distance_km: number;
  lat?: number;
  lng?: number;
}

interface POIResult {
  schools?: POI[];
  hospitals?: POI[];
  malls?: POI[];
  metro_stations?: POI[];
  highways?: POI[];
  bus_depots?: POI[];
  error?: string | null;
}

interface LocationIntelligenceTabProps {
  pois: POIResult | null;
  isLoading: boolean;
  lat: number;
  lng: number;
}

const CATEGORY_ICONS: Record<string, React.FC<{ className?: string }>> = {
  schools: School,
  hospitals: Building2,
  malls: ShoppingBag,
  metro_stations: Train,
  highways: Route,
  bus_depots: Bus,
};

const CATEGORY_LABELS: Record<string, string> = {
  schools: "Schools",
  hospitals: "Hospitals",
  malls: "Malls",
  metro_stations: "Metro Stations",
  highways: "Highways",
  bus_depots: "Bus Depots",
};

export default function LocationIntelligenceTab({ pois, isLoading, lat, lng }: LocationIntelligenceTabProps) {
  const [mapType, setMapType] = useState<"roadmap" | "satellite">("roadmap");
  const [visibleCategories, setVisibleCategories] = useState<Set<string>>(
    new Set(Object.keys(CATEGORY_LABELS))
  );

  function toggleCategory(cat: string) {
    setVisibleCategories((prev) => {
      const next = new Set(prev);
      if (next.has(cat)) next.delete(cat);
      else next.add(cat);
      return next;
    });
  }

  const mapSrc = `https://maps.googleapis.com/maps/api/staticmap?center=${lat},${lng}&zoom=13&size=600x300&maptype=${mapType}&markers=color:red%7C${lat},${lng}&key=${import.meta.env.VITE_GOOGLE_MAPS_API_KEY ?? ""}`;

  return (
    <div className="space-y-6">
      {/* Map with toggle */}
      <div className="relative rounded-xl overflow-hidden border border-white/10 h-52 bg-white/5">
        {import.meta.env.VITE_GOOGLE_MAPS_API_KEY ? (
          <img src={mapSrc} alt="Location map" className="w-full h-full object-cover" />
        ) : (
          <div className="flex items-center justify-center h-full text-white/30 text-sm">
            Map requires VITE_GOOGLE_MAPS_API_KEY
          </div>
        )}
        <div className="absolute bottom-3 right-3 flex gap-1">
          {(["roadmap", "satellite"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setMapType(t)}
              className={`px-2 py-1 text-xs font-medium rounded transition-colors ${
                mapType === t
                  ? "bg-white text-black"
                  : "bg-black/60 text-white/70 border border-white/20 hover:bg-black/80"
              }`}
            >
              {t === "roadmap" ? "Map" : "Satellite"}
            </button>
          ))}
        </div>
      </div>

      {/* POI category toggles */}
      <div>
        <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider mb-2">POI Overlay</h3>
        <div className="flex flex-wrap gap-2">
          {Object.entries(CATEGORY_LABELS).map(([cat, label]) => {
            const Icon = CATEGORY_ICONS[cat];
            return (
              <button
                key={cat}
                onClick={() => toggleCategory(cat)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
                  visibleCategories.has(cat)
                    ? "bg-white text-black border-white"
                    : "bg-white/5 text-white/50 border-white/10 hover:border-white/20"
                }`}
              >
                <Icon className="h-3 w-3" />
                {label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Distance summary table */}
      {isLoading ? (
        <div className="text-center py-6 text-white/30 text-sm">Loading nearby places...</div>
      ) : pois ? (
        <div>
          <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider mb-3">Nearest POIs</h3>
          {pois.error && (
            <p className="text-xs text-yellow-400/70 mb-2">⚠ POI data may be incomplete: {pois.error}</p>
          )}
          <div className="space-y-2">
            {Object.entries(CATEGORY_LABELS).map(([cat, label]) => {
              if (!visibleCategories.has(cat)) return null;
              const items = (pois as any)[cat] as POI[] | undefined;
              const nearest = items?.[0];
              const Icon = CATEGORY_ICONS[cat];
              return (
                <div key={cat} className="flex items-center gap-3 p-3 bg-white/3 border border-white/10 rounded-lg">
                  <Icon className="h-4 w-4 text-white/40 shrink-0" />
                  <span className="flex-1 text-sm text-white">{label}</span>
                  {nearest ? (
                    <div className="text-right">
                      <p className="text-xs text-white font-medium truncate max-w-32">{nearest.name}</p>
                      <p className="text-xs text-white/40">{nearest.distance_km.toFixed(1)} km</p>
                    </div>
                  ) : (
                    <span className="text-xs text-white/20">None found</span>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      ) : null}

      {/* Flood risk overlay notice */}
      <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg text-xs text-blue-300/70">
        Flood risk overlay uses NDMA Hyderabad hazard zone data. Consult HMDA for authoritative flood maps.
      </div>
    </div>
  );
}
