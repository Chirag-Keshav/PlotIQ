import { useNavigate } from "react-router-dom";
import { useMapStore } from "../stores/mapStore";
import { useSearch } from "../hooks/useSearch";
import MapView from "../components/map/MapView";
import SearchBar from "../components/search/SearchBar";
import FilterPanel from "../components/search/FilterPanel";
import ListingCard from "../components/listing/ListingCard";
import SkeletonCard from "../components/listing/SkeletonCard";
import DisclaimerBanner from "../components/ui/DisclaimerBanner";
import Navbar from "../components/Navbar";

export default function DiscoverPage() {
  const navigate = useNavigate();
  const { searchQuery, activeFilters, bounds } = useMapStore();

  const { data, isLoading } = useSearch({
    query: searchQuery,
    filters: { ...activeFilters, bounds },
  });

  const listings = data?.results ?? data?.items ?? [];

  return (
    <div className="flex flex-col h-screen w-full bg-black text-white overflow-hidden">
      <Navbar />

      <div className="flex flex-1 overflow-hidden pt-20">
        {/* Sidebar — 40% on desktop */}
        <div className="w-full md:w-2/5 flex flex-col h-full border-r border-white/10 bg-black/80 backdrop-blur-md overflow-hidden">
          <div className="p-4 border-b border-white/10 space-y-3">
            <DisclaimerBanner variant="score" />
            <SearchBar />
            <FilterPanel />
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {isLoading ? (
              <>
                <SkeletonCard />
                <SkeletonCard />
                <SkeletonCard />
              </>
            ) : listings.length > 0 ? (
              <>
                <p className="text-xs text-white/30 px-1">{listings.length} plot{listings.length !== 1 ? "s" : ""} found</p>
                {listings.map((listing: any, i: number) => (
                  <div
                    key={listing.id}
                    style={{ animation: `stagger-in 0.4s ease-out ${i * 0.05}s both` }}
                  >
                    <ListingCard listing={listing} />
                  </div>
                ))}
              </>
            ) : (
              <div className="text-center py-16 text-white/30">
                <p className="text-4xl mb-3">🗺️</p>
                <p className="font-medium">No verified plots found</p>
                <p className="text-sm mt-1">Try a natural language search like "2 acres near ORR"</p>
              </div>
            )}
          </div>
        </div>

        {/* Map — 60% on desktop, hidden on mobile */}
        <div className="hidden md:block w-3/5 relative h-full">
          <MapView
            listings={listings}
            onListingClick={(id) => navigate(`/listings/${id}`)}
          />
        </div>
      </div>
    </div>
  );
}
