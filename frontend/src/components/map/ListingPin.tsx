import { OverlayView } from "@react-google-maps/api";

interface ListingPinProps {
  lat: number;
  lng: number;
  score: number | null;
  selected?: boolean;
  onClick?: () => void;
}

function scoreColor(score: number | null): string {
  if (score === null) return "#ffffff66";
  if (score >= 80) return "#4ade80";
  if (score >= 50) return "#facc15";
  return "#f87171";
}

export default function ListingPin({ lat, lng, score, selected, onClick }: ListingPinProps) {
  const color = scoreColor(score);

  return (
    <OverlayView
      position={{ lat, lng }}
      mapPaneName={OverlayView.OVERLAY_MOUSE_TARGET}
    >
      <div
        onClick={onClick}
        className="cursor-pointer -translate-x-1/2 -translate-y-1/2"
        style={{ transform: "translate(-50%, -50%)" }}
      >
        <div
          className="flex items-center justify-center rounded-full border-2 font-bold text-black text-xs transition-transform hover:scale-110"
          style={{
            backgroundColor: color,
            borderColor: selected ? "#fff" : color,
            width: selected ? 44 : 36,
            height: selected ? 44 : 36,
            fontSize: selected ? 11 : 10,
            boxShadow: selected ? `0 0 0 3px ${color}66` : "none",
          }}
        >
          {score ?? "?"}
        </div>
      </div>
    </OverlayView>
  );
}
