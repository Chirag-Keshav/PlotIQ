import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion } from "motion/react";
import api from "../lib/api";
import Navbar from "../components/Navbar";
import { CheckCircle2, XCircle, FileQuestion, ShieldX, AlertTriangle } from "lucide-react";

interface QueueItem {
  listing_id: string;
  title: string;
  locality: string;
  confidence_score: number | null;
  fraud_signals: Array<{ type: string; severity: string }>;
  created_at: string;
}

interface Metrics {
  total_listings: number;
  live_listings: number;
  pending_review_listings: number;
  verification_rate_pct: number;
  fraud_catch_rate_pct: number;
  stale_listing_count: number;
}

export default function AdminDashboard() {
  const [actionNote, setActionNote] = useState("");
  const qc = useQueryClient();

  const { data: metricsData } = useQuery<Metrics>({
    queryKey: ["admin", "metrics"],
    queryFn: async () => {
      const { data } = await api.get("/admin/metrics");
      return data;
    },
  });

  const { data: queueData, isLoading: queueLoading } = useQuery<{ queue: QueueItem[]; total: number }>({
    queryKey: ["admin", "queue"],
    queryFn: async () => {
      const { data } = await api.get("/admin/queue");
      return data;
    },
  });

  const actionMutation = useMutation({
    mutationFn: async ({ listingId, action }: { listingId: string; action: string }) => {
      const { data } = await api.post(`/admin/listings/${listingId}/action`, {
        action,
        note: actionNote || undefined,
      });
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin"] });
      setActionNote("");
    },
  });

  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />
      <div className="max-w-6xl mx-auto px-6 pt-28 pb-16 space-y-8">
        <motion.h1
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-3xl font-bold"
        >
          Admin Trust Dashboard
        </motion.h1>

        {/* Metrics panel */}
        {metricsData && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3"
          >
            {[
              { label: "Total Listings", value: metricsData.total_listings },
              { label: "Live", value: metricsData.live_listings },
              { label: "Pending Review", value: metricsData.pending_review_listings, warn: metricsData.pending_review_listings > 0 },
              { label: "Verification Rate", value: `${metricsData.verification_rate_pct?.toFixed(1)}%` },
              { label: "Fraud Catch Rate", value: `${metricsData.fraud_catch_rate_pct?.toFixed(1)}%` },
              { label: "Stale Listings", value: metricsData.stale_listing_count, warn: metricsData.stale_listing_count > 0 },
            ].map(({ label, value, warn }) => (
              <div
                key={label}
                className={`p-4 border rounded-xl text-center ${
                  warn ? "bg-yellow-500/10 border-yellow-500/20" : "bg-white/3 border-white/10"
                }`}
              >
                <p className="text-2xl font-bold font-mono text-white">{value}</p>
                <p className="text-xs text-white/40 mt-1">{label}</p>
              </div>
            ))}
          </motion.div>
        )}

        {/* Verification queue */}
        <div>
          <h2 className="text-lg font-semibold mb-4">Verification Queue</h2>

          {queueLoading ? (
            <div className="text-white/30 text-center py-8">Loading queue...</div>
          ) : !queueData?.queue?.length ? (
            <div className="p-8 text-center text-white/30 bg-white/3 border border-white/10 rounded-xl">
              <CheckCircle2 className="h-8 w-8 mx-auto mb-2 text-green-400" />
              Queue is empty — no listings pending review.
            </div>
          ) : (
            <div className="space-y-3">
              {queueData.queue.map((item) => (
                <div key={item.listing_id} className="p-4 bg-white/3 border border-white/10 rounded-xl">
                  <div className="flex flex-wrap justify-between items-start gap-3 mb-3">
                    <div>
                      <p className="font-semibold text-white">{item.title}</p>
                      <p className="text-sm text-white/50">{item.locality}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      {item.confidence_score !== null && (
                        <span
                          className={`px-2 py-0.5 rounded text-xs font-bold border ${
                            (item.confidence_score ?? 0) >= 70
                              ? "bg-green-500/20 text-green-400 border-green-500/30"
                              : "bg-red-500/20 text-red-400 border-red-500/30"
                          }`}
                        >
                          Score: {item.confidence_score}
                        </span>
                      )}
                      {item.fraud_signals?.map((f, i) => (
                        <span
                          key={i}
                          className="flex items-center gap-1 px-2 py-0.5 rounded text-xs border bg-red-500/10 text-red-400 border-red-500/20"
                        >
                          <AlertTriangle className="h-3 w-3" />
                          {f.type.replace(/_/g, " ")}
                        </span>
                      ))}
                    </div>
                  </div>

                  <input
                    type="text"
                    placeholder="Optional note..."
                    value={actionNote}
                    onChange={(e) => setActionNote(e.target.value)}
                    className="w-full mb-3 px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder-white/20 focus:outline-none focus:border-white/20"
                  />

                  <div className="flex flex-wrap gap-2">
                    <button
                      onClick={() => actionMutation.mutate({ listingId: item.listing_id, action: "approve" })}
                      className="flex items-center gap-1.5 px-3 py-1.5 bg-green-500/20 border border-green-500/30 text-green-400 text-xs font-bold rounded-lg hover:bg-green-500/30 transition-colors"
                    >
                      <CheckCircle2 className="h-3.5 w-3.5" /> Approve
                    </button>
                    <button
                      onClick={() => actionMutation.mutate({ listingId: item.listing_id, action: "request_docs" })}
                      className="flex items-center gap-1.5 px-3 py-1.5 bg-yellow-500/20 border border-yellow-500/30 text-yellow-400 text-xs font-bold rounded-lg hover:bg-yellow-500/30 transition-colors"
                    >
                      <FileQuestion className="h-3.5 w-3.5" /> Request Docs
                    </button>
                    <button
                      onClick={() => actionMutation.mutate({ listingId: item.listing_id, action: "reject" })}
                      className="flex items-center gap-1.5 px-3 py-1.5 bg-red-500/20 border border-red-500/30 text-red-400 text-xs font-bold rounded-lg hover:bg-red-500/30 transition-colors"
                    >
                      <XCircle className="h-3.5 w-3.5" /> Reject
                    </button>
                    <button
                      onClick={() => actionMutation.mutate({ listingId: item.listing_id, action: "mark_scam" })}
                      className="flex items-center gap-1.5 px-3 py-1.5 bg-red-900/30 border border-red-900/40 text-red-300 text-xs font-bold rounded-lg hover:bg-red-900/50 transition-colors"
                    >
                      <ShieldX className="h-3.5 w-3.5" /> Mark Scam
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
