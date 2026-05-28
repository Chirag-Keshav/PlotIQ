import { useState } from "react";
import { MapPin } from "lucide-react";

interface Step1Props {
  lat: number | null;
  lng: number | null;
  onChange: (lat: number, lng: number) => void;
}

export default function Step1LocationPicker({ lat, lng, onChange }: Step1Props) {
  const [draftLat, setDraftLat] = useState(lat?.toString() ?? "");
  const [draftLng, setDraftLng] = useState(lng?.toString() ?? "");

  function apply() {
    const parsedLat = parseFloat(draftLat);
    const parsedLng = parseFloat(draftLng);
    if (!isNaN(parsedLat) && !isNaN(parsedLng)) {
      onChange(parsedLat, parsedLng);
    }
  }

  return (
    <div className="space-y-5">
      <div className="p-4 bg-white/3 border border-white/10 rounded-xl flex items-center justify-center h-48 text-white/30 text-sm flex-col gap-2">
        <MapPin className="h-8 w-8" />
        <span>Google Maps pin drop</span>
        <span className="text-xs">(requires VITE_GOOGLE_MAPS_API_KEY)</span>
      </div>

      <p className="text-xs text-white/40 text-center">Or enter coordinates manually</p>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="text-xs text-white/50 mb-1 block">Latitude</label>
          <input
            type="number"
            step="0.0001"
            placeholder="17.3850"
            value={draftLat}
            onChange={(e) => setDraftLat(e.target.value)}
            className="w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white text-sm placeholder-white/20 focus:outline-none focus:border-white/30"
          />
        </div>
        <div>
          <label className="text-xs text-white/50 mb-1 block">Longitude</label>
          <input
            type="number"
            step="0.0001"
            placeholder="78.4867"
            value={draftLng}
            onChange={(e) => setDraftLng(e.target.value)}
            className="w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white text-sm placeholder-white/20 focus:outline-none focus:border-white/30"
          />
        </div>
      </div>

      <button
        type="button"
        onClick={apply}
        className="btn-secondary w-full text-sm"
        disabled={!draftLat || !draftLng}
      >
        Confirm Location
      </button>

      {lat !== null && lng !== null && (
        <p className="text-xs text-green-400 text-center">
          ✓ Location set: {lat.toFixed(4)}, {lng.toFixed(4)}
        </p>
      )}
    </div>
  );
}
