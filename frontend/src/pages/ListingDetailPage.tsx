import { useState } from "react";
import { useParams } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { Flag } from "lucide-react";
import api from "../lib/api";
import { useAuth } from "@clerk/clerk-react";
import { useListing } from "../hooks/useListing";
import {
  useListingScore,
  useListingPriceEstimate,
  useListingPOIs,
  useListingGrowthSignals,
} from "../hooks/useListingScore";
import Navbar from "../components/Navbar";
import BreadcrumbNav from "../components/listing/BreadcrumbNav";
import ListingHeader from "../components/listing/ListingHeader";
import OverviewTab from "../components/listing/tabs/OverviewTab";
import AIScoreTab from "../components/listing/tabs/AIScoreTab";
import LegalDocsTab from "../components/listing/tabs/LegalDocsTab";
import PriceIntelligenceTab from "../components/listing/tabs/PriceIntelligenceTab";
import LocationIntelligenceTab from "../components/listing/tabs/LocationIntelligenceTab";
import FutureGrowthTab from "../components/listing/tabs/FutureGrowthTab";
import RiskSummaryTab from "../components/listing/tabs/RiskSummaryTab";

const TABS = [
  { id: "overview", label: "Overview" },
  { id: "score", label: "AI Score" },
  { id: "legal", label: "Legal & Docs" },
  { id: "price", label: "Price Intel" },
  { id: "location", label: "Location" },
  { id: "growth", label: "Future Growth" },
  { id: "risk", label: "Risk Summary" },
];

export default function ListingDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [activeTab, setActiveTab] = useState("overview");

  const { isSignedIn } = useAuth();
  const [reportSent, setReportSent] = useState(false);

  const { data: listing, isLoading } = useListing(id ?? null);
  const { data: scoreData } = useListingScore(id ?? null);

  const reportMutation = useMutation({
    mutationFn: () =>
      api.post(`/listings/${id}/report`, { reason: "user_report", description: "Reported by user" }),
    onSuccess: () => setReportSent(true),
  });
  const { data: priceData, isLoading: priceLoading } = useListingPriceEstimate(id ?? null);
  const { data: poisData, isLoading: poisLoading } = useListingPOIs(id ?? null);
  const { data: growthData, isLoading: growthLoading } = useListingGrowthSignals(id ?? null);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-white/40">Loading listing...</div>
      </div>
    );
  }

  if (!listing) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-white/40">Listing not found</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />
      <div className="max-w-5xl mx-auto px-6 pt-28 pb-16">
        <BreadcrumbNav />

        <ListingHeader
          title={listing.title}
          locality={listing.locality}
          price_lakhs={listing.price_lakhs}
          area_sqyd={listing.area_sqyd}
          verification_tier={listing.verification_tier ?? "unverified"}
          listing_status={listing.listing_status}
          created_at={listing.created_at}
        />

        {/* Report listing */}
        {isSignedIn && (
          <div className="mb-4 flex justify-end">
            {reportSent ? (
              <span className="text-xs text-green-400">✓ Report submitted</span>
            ) : (
              <button
                onClick={() => reportMutation.mutate()}
                disabled={reportMutation.isPending}
                className="flex items-center gap-1.5 text-xs text-white/30 hover:text-red-400 transition-colors disabled:opacity-50"
              >
                <Flag className="h-3 w-3" />
                {reportMutation.isPending ? "Reporting..." : "Report this listing"}
              </button>
            )}
          </div>
        )}

        {/* Tab nav */}
        <div className="flex gap-1 overflow-x-auto border-b border-white/10 mb-8 pb-px">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2.5 whitespace-nowrap text-sm font-medium transition-colors rounded-t-lg ${
                activeTab === tab.id
                  ? "text-white border-b-2 border-white"
                  : "text-white/40 hover:text-white/70"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab content */}
        <div className="min-h-96">
          {activeTab === "overview" && <OverviewTab listing={listing} />}
          {activeTab === "score" && (
            <AIScoreTab
              score={scoreData?.confidence_score ?? listing.confidence_score}
              breakdown={scoreData?.breakdown ?? listing.confidence_breakdown}
            />
          )}
          {activeTab === "legal" && (
            <LegalDocsTab documents={listing.documents ?? []} />
          )}
          {activeTab === "price" && (
            <PriceIntelligenceTab data={priceData ?? null} isLoading={priceLoading} />
          )}
          {activeTab === "location" && (
            <LocationIntelligenceTab
              pois={poisData ?? null}
              isLoading={poisLoading}
              lat={listing.lat}
              lng={listing.lng}
            />
          )}
          {activeTab === "growth" && (
            <FutureGrowthTab
              growthTier={growthData?.growth_tier ?? null}
              signals={growthData?.signals ?? []}
              isLoading={growthLoading}
            />
          )}
          {activeTab === "risk" && (
            <RiskSummaryTab
              riskFlags={listing.risk_flags ?? []}
              documents={listing.documents ?? []}
            />
          )}
        </div>
      </div>
    </div>
  );
}
