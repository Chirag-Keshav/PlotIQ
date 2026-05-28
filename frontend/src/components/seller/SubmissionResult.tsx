import { CheckCircle2, AlertCircle, ArrowRight } from "lucide-react";
import { useNavigate } from "react-router-dom";

interface SubmissionResultProps {
  listingId: string;
  confidence_score: number | null;
  listing_status: string;
  message: string;
}

export default function SubmissionResult({
  listingId,
  confidence_score,
  listing_status,
  message,
}: SubmissionResultProps) {
  const navigate = useNavigate();

  const isLive = listing_status === "live";

  return (
    <div className="text-center space-y-6">
      <div className="flex justify-center">
        {isLive ? (
          <CheckCircle2 className="h-16 w-16 text-green-400" />
        ) : (
          <AlertCircle className="h-16 w-16 text-yellow-400" />
        )}
      </div>

      <div>
        <h2 className="text-2xl font-bold text-white mb-2">
          {isLive ? "Listing is Live!" : "Listing Submitted for Review"}
        </h2>
        <p className="text-white/60 text-sm">{message}</p>
      </div>

      {confidence_score !== null && (
        <div className="p-4 bg-white/3 border border-white/10 rounded-xl inline-block">
          <p className="text-xs text-white/40 mb-1">Preliminary Confidence Score</p>
          <p
            className="text-4xl font-bold font-mono"
            style={{
              color:
                confidence_score >= 80
                  ? "#4ade80"
                  : confidence_score >= 50
                  ? "#facc15"
                  : "#f87171",
            }}
          >
            {confidence_score}
          </p>
        </div>
      )}

      {listing_status === "pending_review" && (
        <div className="p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg text-yellow-300 text-sm">
          Your listing is under review. Upload more documents to improve your score and get live faster.
        </div>
      )}

      <button
        onClick={() => navigate(`/listings/${listingId}`)}
        className="btn-primary flex items-center gap-2 mx-auto"
      >
        View Your Listing <ArrowRight className="h-4 w-4" />
      </button>
    </div>
  );
}
