import { useCallback, useRef, useState } from "react";
import { GoogleMap, useJsApiLoader } from "@react-google-maps/api";
import { useMapStore } from "../../stores/mapStore";
import ListingPin from "./ListingPin";
import SearchAreaButton from "./SearchAreaButton";

interface MapListing {
  id: string;
  lat: number;
  lng: number;
  confidence_score: number | null;
}

interface MapViewProps {
  listings: MapListing[];
  onListingClick?: (id: string) => void;
}

const MAP_STYLES: google.maps.MapTypeStyle[] = [
  { elementType: "geometry", stylers: [{ color: "#0a0a0a" }] },
  { elementType: "labels.text.stroke", stylers: [{ color: "#0a0a0a" }] },
  { elementType: "labels.text.fill", stylers: [{ color: "#555" }] },
  { featureType: "road", elementType: "geometry", stylers: [{ color: "#1a1a1a" }] },
  { featureType: "road", elementType: "geometry.stroke", stylers: [{ color: "#212121" }] },
  { featureType: "water", elementType: "geometry", stylers: [{ color: "#000000" }] },
  { featureType: "poi", stylers: [{ visibility: "off" }] },
  { featureType: "transit", stylers: [{ visibility: "off" }] },
];

const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY ?? "";

export default function MapView({ listings, onListingClick }: MapViewProps) {
  const { center, zoom, setBounds, setCenter, setZoom, selectedListingId, setSelectedListing } = useMapStore();
  const [showSearchBtn, setShowSearchBtn] = useState(false);
  const hasPanned = useRef(false);

  const { isLoaded } = useJsApiLoader({
    googleMapsApiKey: GOOGLE_MAPS_API_KEY,
    id: "google-map-script",
  });

  const onBoundsChanged = useCallback(() => {
    if (hasPanned.current) setShowSearchBtn(true);
  }, []);

  const onDragEnd = useCallback(() => {
    hasPanned.current = true;
    setShowSearchBtn(true);
  }, []);

  const onIdle = useCallback((map: google.maps.Map) => {
    const b = map.getBounds();
    if (b) {
      const ne = b.getNorthEast();
      const sw = b.getSouthWest();
      setBounds({ north: ne.lat(), south: sw.lat(), east: ne.lng(), west: sw.lng() });
    }
    const c = map.getCenter();
    if (c) setCenter({ lat: c.lat(), lng: c.lng() });
    setZoom(map.getZoom() ?? 11);
  }, [setBounds, setCenter, setZoom]);

  const handleSearchArea = useCallback(() => {
    setShowSearchBtn(false);
    hasPanned.current = false;
  }, []);

  if (!isLoaded || !GOOGLE_MAPS_API_KEY) {
    return (
      <div className="w-full h-full bg-black/90 flex flex-col items-center justify-center text-white/30 gap-2">
        <div className="text-4xl">🗺️</div>
        <p className="text-sm">
          {!GOOGLE_MAPS_API_KEY
            ? "Set VITE_GOOGLE_MAPS_API_KEY to enable map"
            : "Loading map..."}
        </p>
      </div>
    );
  }

  return (
    <div className="relative w-full h-full">
      <GoogleMap
        mapContainerStyle={{ width: "100%", height: "100%" }}
        center={center}
        zoom={zoom}
        options={{
          styles: MAP_STYLES,
          disableDefaultUI: false,
          zoomControl: true,
          mapTypeControl: false,
          streetViewControl: false,
          fullscreenControl: false,
        }}
        onDragEnd={onDragEnd}
        onBoundsChanged={onBoundsChanged}
        onIdle={(map) => onIdle(map as unknown as google.maps.Map)}
      >
        {listings.map((l) => (
          <ListingPin
            key={l.id}
            lat={l.lat}
            lng={l.lng}
            score={l.confidence_score}
            selected={l.id === selectedListingId}
            onClick={() => {
              setSelectedListing(l.id);
              onListingClick?.(l.id);
            }}
          />
        ))}
      </GoogleMap>

      <SearchAreaButton visible={showSearchBtn} onClick={handleSearchArea} />
    </div>
  );
}
