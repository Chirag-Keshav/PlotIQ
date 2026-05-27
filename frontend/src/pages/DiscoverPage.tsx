import React from 'react';
import { useMapStore } from '../stores/mapStore';
import { useSearch } from '../hooks/useSearch';
// import MapView from '../components/map/MapView';
// import SearchBar from '../components/search/SearchBar';
// import FilterPanel from '../components/search/FilterPanel';
// import ListingCard from '../components/listing/ListingCard';
// import SkeletonCard from '../components/listing/SkeletonCard';
// import DisclaimerBanner from '../components/ui/DisclaimerBanner';

export default function DiscoverPage() {
  const { searchQuery, activeFilters, bounds } = useMapStore();
  
  const { data, isLoading } = useSearch({
    query: searchQuery,
    filters: { ...activeFilters, bounds }
  });

  return (
    <div className="flex h-screen w-full bg-black text-white pt-20">
      {/* Sidebar - 40% on desktop */}
      <div className="w-full md:w-2/5 flex flex-col h-full border-r border-white/10 relative z-10 bg-black/80 backdrop-blur-md">
        <div className="p-4 border-b border-white/10 space-y-4">
          {/* <DisclaimerBanner variant="score" /> */}
          {/* <SearchBar /> */}
          {/* <FilterPanel /> */}
        </div>
        
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {isLoading ? (
            <>
              {/* <SkeletonCard /> */}
              {/* <SkeletonCard /> */}
              <div className="text-white/50 text-center py-8">Loading AI Analysis...</div>
            </>
          ) : data?.items?.length ? (
            data.items.map((listing: any) => (
              <div key={listing.id} className="p-4 bg-white/5 border border-white/10 rounded-xl">
                <h3 className="font-bold">{listing.title}</h3>
                <p className="text-sm text-white/60">{listing.locality} • {listing.area_sqyd} sqyd</p>
                <div className="mt-2 flex justify-between items-center">
                  <span className="text-xl font-bold font-mono">₹{listing.price_lakhs}L</span>
                  <span className={`px-2 py-1 rounded text-xs font-bold ${
                    listing.confidence_score >= 80 ? 'bg-green-500/20 text-green-400' :
                    listing.confidence_score >= 50 ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-red-500/20 text-red-400'
                  }`}>
                    SCORE: {listing.confidence_score}
                  </span>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-12 text-white/40">
              <p>No verified plots found.</p>
              <p className="text-sm mt-2">Try adjusting your filters or expanding the map area.</p>
            </div>
          )}
        </div>
      </div>
      
      {/* Map - 60% on desktop */}
      <div className="hidden md:block w-3/5 relative h-full">
        <div className="absolute inset-0 bg-black/90 flex items-center justify-center text-white/50">
          {/* <MapView listings={data?.items || []} /> */}
          Map View Placeholder
        </div>
        {/* <SearchAreaButton /> */}
      </div>
    </div>
  );
}
