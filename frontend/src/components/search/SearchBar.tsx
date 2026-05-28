import { useState } from "react";
import { Search } from "lucide-react";
import { useMapStore } from "../../stores/mapStore";

export default function SearchBar() {
  const { searchQuery, setSearchQuery } = useMapStore();
  const [draft, setDraft] = useState(searchQuery);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSearchQuery(draft.trim());
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-white/40" />
        <input
          type="text"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="e.g. 2 acres near ORR under 50 lakhs..."
          className="w-full pl-9 pr-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white text-sm placeholder-white/30 focus:outline-none focus:border-white/30 focus:bg-white/8 transition-colors"
        />
      </div>
      <button type="submit" className="btn-primary text-sm px-4 py-2.5">
        Search
      </button>
    </form>
  );
}
