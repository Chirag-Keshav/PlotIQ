import { Link } from "react-router-dom";
import { ChevronLeft } from "lucide-react";

export default function BreadcrumbNav() {
  return (
    <Link
      to="/discover"
      className="inline-flex items-center gap-1 text-white/50 hover:text-white text-sm transition-colors mb-6"
    >
      <ChevronLeft className="h-4 w-4" />
      Back to Map
    </Link>
  );
}
