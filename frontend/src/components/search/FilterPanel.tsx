import { useState } from "react";
import { SlidersHorizontal, ChevronDown, ChevronUp } from "lucide-react";
import { useMapStore } from "../../stores/mapStore";

const LOCALITIES = [
  "Kokapet", "Shadnagar", "Adibatla", "Patancheru",
  "Ibrahimpatnam", "Shamshabad", "Ghatkesar", "Sangareddy",
];

const USE_TYPES = [
  { value: "", label: "Any" },
  { value: "residential", label: "Residential" },
  { value: "commercial", label: "Commercial" },
  { value: "agricultural", label: "Agricultural" },
];

export default function FilterPanel() {
  const [open, setOpen] = useState(false);
  const { activeFilters, setFilters } = useMapStore();

  function handleLocality(loc: string) {
    const current = activeFilters.localities ?? [];
    const next = current.includes(loc)
      ? current.filter((l) => l !== loc)
      : [...current, loc];
    setFilters({ localities: next });
  }

  return (
    <div>
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-2 text-sm text-white/60 hover:text-white transition-colors"
      >
        <SlidersHorizontal className="h-4 w-4" />
        Filters
        {open ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
      </button>

      {open && (
        <div className="mt-3 p-4 bg-white/3 border border-white/10 rounded-xl space-y-4">
          {/* Price range */}
          <div>
            <label className="text-xs text-white/50 uppercase tracking-wider mb-2 block">
              Price (Lakhs)
            </label>
            <div className="flex gap-2">
              <input
                type="number"
                placeholder="Min"
                value={activeFilters.budget_min ?? ""}
                onChange={(e) =>
                  setFilters({ budget_min: e.target.value ? Number(e.target.value) : undefined })
                }
                className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-sm placeholder-white/30 focus:outline-none focus:border-white/20"
              />
              <input
                type="number"
                placeholder="Max"
                value={activeFilters.budget_max ?? ""}
                onChange={(e) =>
                  setFilters({ budget_max: e.target.value ? Number(e.target.value) : undefined })
                }
                className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-sm placeholder-white/30 focus:outline-none focus:border-white/20"
              />
            </div>
          </div>

          {/* Area range */}
          <div>
            <label className="text-xs text-white/50 uppercase tracking-wider mb-2 block">
              Area (sqyd)
            </label>
            <div className="flex gap-2">
              <input
                type="number"
                placeholder="Min"
                value={activeFilters.area_min ?? ""}
                onChange={(e) =>
                  setFilters({ area_min: e.target.value ? Number(e.target.value) : undefined })
                }
                className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-sm placeholder-white/30 focus:outline-none focus:border-white/20"
              />
              <input
                type="number"
                placeholder="Max"
                value={activeFilters.area_max ?? ""}
                onChange={(e) =>
                  setFilters({ area_max: e.target.value ? Number(e.target.value) : undefined })
                }
                className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-sm placeholder-white/30 focus:outline-none focus:border-white/20"
              />
            </div>
          </div>

          {/* Locality */}
          <div>
            <label className="text-xs text-white/50 uppercase tracking-wider mb-2 block">
              Locality
            </label>
            <div className="flex flex-wrap gap-2">
              {LOCALITIES.map((loc) => (
                <button
                  key={loc}
                  onClick={() => handleLocality(loc)}
                  className={`px-3 py-1 rounded-full text-xs font-medium border transition-colors ${
                    (activeFilters.localities ?? []).includes(loc)
                      ? "bg-white text-black border-white"
                      : "bg-white/5 text-white/60 border-white/10 hover:border-white/20"
                  }`}
                >
                  {loc}
                </button>
              ))}
            </div>
          </div>

          {/* Use type */}
          <div>
            <label className="text-xs text-white/50 uppercase tracking-wider mb-2 block">
              Use Type
            </label>
            <div className="flex flex-wrap gap-2">
              {USE_TYPES.map((ut) => (
                <button
                  key={ut.value}
                  onClick={() => setFilters({ use_type: ut.value || undefined })}
                  className={`px-3 py-1 rounded-full text-xs font-medium border transition-colors ${
                    (activeFilters.use_type ?? "") === ut.value
                      ? "bg-white text-black border-white"
                      : "bg-white/5 text-white/60 border-white/10 hover:border-white/20"
                  }`}
                >
                  {ut.label}
                </button>
              ))}
            </div>
          </div>

          {/* Confidence score threshold */}
          <div>
            <label className="text-xs text-white/50 uppercase tracking-wider mb-2 block">
              Min Confidence Score: {activeFilters.confidence_min ?? 0}
            </label>
            <input
              type="range"
              min={0}
              max={100}
              step={5}
              value={activeFilters.confidence_min ?? 0}
              onChange={(e) =>
                setFilters({ confidence_min: Number(e.target.value) || undefined })
              }
              className="w-full accent-white"
            />
          </div>

          <button
            onClick={() =>
              setFilters({
                budget_min: undefined,
                budget_max: undefined,
                area_min: undefined,
                area_max: undefined,
                localities: [],
                use_type: undefined,
                confidence_min: undefined,
              })
            }
            className="text-xs text-white/40 hover:text-white transition-colors"
          >
            Clear all filters
          </button>
        </div>
      )}
    </div>
  );
}
