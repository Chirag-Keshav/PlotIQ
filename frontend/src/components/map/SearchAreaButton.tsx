import { Search } from "lucide-react";

interface SearchAreaButtonProps {
  visible: boolean;
  onClick: () => void;
}

export default function SearchAreaButton({ visible, onClick }: SearchAreaButtonProps) {
  if (!visible) return null;

  return (
    <div className="absolute top-4 left-1/2 -translate-x-1/2 z-10">
      <button
        onClick={onClick}
        className="flex items-center gap-2 px-4 py-2 bg-black/80 backdrop-blur-md border border-white/20 text-white text-sm font-semibold rounded-full shadow-lg hover:bg-black/90 transition-colors"
      >
        <Search className="h-4 w-4" />
        Search this area
      </button>
    </div>
  );
}
