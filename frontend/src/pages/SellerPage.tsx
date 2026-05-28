import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import api from "../lib/api";
import Navbar from "../components/Navbar";
import Step1LocationPicker from "../components/seller/Step1LocationPicker";
import Step2PlotDetails from "../components/seller/Step2PlotDetails";
import Step3DocumentUpload from "../components/seller/Step3DocumentUpload";
import SubmissionResult from "../components/seller/SubmissionResult";

interface PlotDetails {
  title: string;
  description: string;
  locality: string;
  price_lakhs: string;
  area_sqyd: string;
  use_type: string;
  road_access: string;
  ownership_type: string;
}

const STEPS = ["Location", "Plot Details", "Documents"];

export default function SellerPage() {
  const [step, setStep] = useState(0);
  const [lat, setLat] = useState<number | null>(null);
  const [lng, setLng] = useState<number | null>(null);
  const [details, setDetails] = useState<PlotDetails>({
    title: "",
    description: "",
    locality: "",
    price_lakhs: "",
    area_sqyd: "",
    use_type: "",
    road_access: "",
    ownership_type: "",
  });
  const [uploads, setUploads] = useState({ ec: null as File | null, sale_deed: null as File | null, photos: [] as File[] });
  const [tosAccepted, setTosAccepted] = useState(false);
  const [result, setResult] = useState<any>(null);

  const mutation = useMutation({
    mutationFn: async () => {
      const payload = {
        ...details,
        lat,
        lng,
        price_lakhs: parseFloat(details.price_lakhs),
        area_sqyd: parseFloat(details.area_sqyd),
        tos_accepted: true,
      };
      const { data } = await api.post("/listings", payload);
      return data;
    },
    onSuccess: (data) => {
      setResult(data);
    },
  });

  function canProceed() {
    if (step === 0) return lat !== null && lng !== null;
    if (step === 1)
      return (
        details.title.trim() &&
        details.locality &&
        details.price_lakhs &&
        details.area_sqyd &&
        details.use_type &&
        details.road_access &&
        details.ownership_type
      );
    if (step === 2) return tosAccepted;
    return false;
  }

  if (result) {
    return (
      <div className="min-h-screen bg-black text-white">
        <Navbar />
        <div className="max-w-xl mx-auto px-6 pt-28 pb-16">
          <SubmissionResult
            listingId={result.id}
            confidence_score={result.confidence_score ?? null}
            listing_status={result.listing_status}
            message={result.message}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />
      <div className="max-w-xl mx-auto px-6 pt-28 pb-16">
        <h1 className="text-3xl font-bold mb-8">List Your Plot</h1>

        {/* Step indicator */}
        <div className="flex items-center gap-2 mb-8">
          {STEPS.map((label, i) => (
            <div key={i} className="flex items-center gap-2">
              <div
                className={`h-7 w-7 rounded-full flex items-center justify-center text-xs font-bold transition-colors ${
                  i === step
                    ? "bg-white text-black"
                    : i < step
                    ? "bg-white/20 text-white"
                    : "bg-white/5 text-white/30"
                }`}
              >
                {i + 1}
              </div>
              <span
                className={`text-sm ${i === step ? "text-white font-medium" : "text-white/40"}`}
              >
                {label}
              </span>
              {i < STEPS.length - 1 && <div className="h-px w-6 bg-white/10" />}
            </div>
          ))}
        </div>

        <div className="glass-card p-6 mb-6">
          {step === 0 && (
            <Step1LocationPicker
              lat={lat}
              lng={lng}
              onChange={(newLat, newLng) => { setLat(newLat); setLng(newLng); }}
            />
          )}
          {step === 1 && (
            <Step2PlotDetails
              details={details}
              onChange={(field, value) => setDetails((d) => ({ ...d, [field]: value }))}
            />
          )}
          {step === 2 && (
            <div className="space-y-6">
              <Step3DocumentUpload uploads={uploads} onChange={setUploads} />
              <label className="flex items-start gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={tosAccepted}
                  onChange={(e) => setTosAccepted(e.target.checked)}
                  className="mt-0.5 accent-white"
                />
                <span className="text-xs text-white/60">
                  I accept the{" "}
                  <a href="/legal" className="text-white underline" target="_blank">
                    Terms of Service
                  </a>{" "}
                  and confirm that all submitted information is accurate to the best of my knowledge.
                </span>
              </label>
            </div>
          )}
        </div>

        {mutation.isError && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
            {(mutation.error as any)?.response?.data?.detail ??
              (mutation.error as any)?.response?.data?.error?.message ??
              "Submission failed. Please try again."}
          </div>
        )}

        <div className="flex justify-between">
          <button
            onClick={() => setStep((s) => s - 1)}
            disabled={step === 0}
            className="btn-secondary text-sm disabled:opacity-30 disabled:cursor-not-allowed"
          >
            Back
          </button>
          {step < STEPS.length - 1 ? (
            <button
              onClick={() => setStep((s) => s + 1)}
              disabled={!canProceed()}
              className="btn-primary text-sm disabled:opacity-30 disabled:cursor-not-allowed"
            >
              Next
            </button>
          ) : (
            <button
              onClick={() => mutation.mutate()}
              disabled={!canProceed() || mutation.isPending}
              className="btn-primary text-sm disabled:opacity-30 disabled:cursor-not-allowed"
            >
              {mutation.isPending ? "Submitting..." : "Submit Listing"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
