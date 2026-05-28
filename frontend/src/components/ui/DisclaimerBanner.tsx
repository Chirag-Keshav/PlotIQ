import { AlertTriangle } from "lucide-react";

interface DisclaimerBannerProps {
  variant: "score" | "price" | "document" | "growth";
}

const DISCLAIMER_TEXT: Record<DisclaimerBannerProps["variant"], string> = {
  score: "AI confidence score is a model estimate and does not constitute legal title certification.",
  price: "Price estimates are model outputs and are not a valuation or guarantee.",
  document: "This is an AI-generated summary only. Consult a licensed lawyer for legal advice and title verification.",
  growth: "Growth signals are based on announced or approved projects. Outcomes depend on execution. This is not investment advice.",
};

export default function DisclaimerBanner({ variant }: DisclaimerBannerProps) {
  return (
    <div className="flex items-start gap-3 px-4 py-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg text-yellow-300 text-sm">
      <AlertTriangle className="h-4 w-4 mt-0.5 shrink-0" />
      <span>{DISCLAIMER_TEXT[variant]}</span>
    </div>
  );
}
