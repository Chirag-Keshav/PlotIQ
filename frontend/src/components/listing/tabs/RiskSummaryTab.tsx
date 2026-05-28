import { AlertTriangle, ShieldAlert, FileX } from "lucide-react";

interface RiskFlag {
  type: string;
  severity: "high" | "medium" | "low";
  detail?: string;
}

interface RiskSummaryTabProps {
  riskFlags: RiskFlag[];
  documents: Array<{ doc_type: string; analysis_status: string }>;
}

const SEVERITY_COLORS: Record<string, string> = {
  high: "bg-red-500/10 border-red-500/30 text-red-400",
  medium: "bg-yellow-500/10 border-yellow-500/30 text-yellow-400",
  low: "bg-white/5 border-white/10 text-white/50",
};

const EXPECTED_DOCS = ["ec", "sale_deed", "layout_approval", "mutation_register", "patta"];
const DOC_LABELS: Record<string, string> = {
  ec: "Encumbrance Certificate",
  sale_deed: "Sale Deed",
  layout_approval: "Layout Approval",
  mutation_register: "Mutation Register",
  patta: "Patta / ROR",
};

export default function RiskSummaryTab({ riskFlags, documents }: RiskSummaryTabProps) {
  const uploadedTypes = new Set(documents.map((d) => d.doc_type));
  const missingDocs = EXPECTED_DOCS.filter((d) => !uploadedTypes.has(d));
  const topFlags = [...riskFlags]
    .sort((a, b) => {
      const order = { high: 0, medium: 1, low: 2 };
      return order[a.severity] - order[b.severity];
    })
    .slice(0, 3);

  return (
    <div className="space-y-6">
      {/* Top risk flags */}
      <div>
        <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider mb-3 flex items-center gap-2">
          <ShieldAlert className="h-4 w-4" /> Risk Flags
        </h3>
        {topFlags.length === 0 ? (
          <div className="p-4 bg-green-500/10 border border-green-500/20 rounded-xl text-green-400 text-sm">
            No risk flags detected.
          </div>
        ) : (
          <div className="space-y-3">
            {topFlags.map((flag, i) => (
              <div
                key={i}
                className={`p-4 border rounded-xl ${SEVERITY_COLORS[flag.severity]}`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <AlertTriangle className="h-4 w-4 shrink-0" />
                  <span className="text-sm font-bold capitalize">
                    {flag.type.replace(/_/g, " ")}
                  </span>
                  <span className="ml-auto text-xs font-bold uppercase tracking-wider opacity-70">
                    {flag.severity}
                  </span>
                </div>
                {flag.detail && (
                  <p className="text-xs opacity-70 mt-1">{flag.detail}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Missing document checklist */}
      <div>
        <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider mb-3 flex items-center gap-2">
          <FileX className="h-4 w-4" /> Missing Documents
        </h3>
        {missingDocs.length === 0 ? (
          <div className="p-4 bg-green-500/10 border border-green-500/20 rounded-xl text-green-400 text-sm">
            All expected documents are uploaded.
          </div>
        ) : (
          <ul className="space-y-2">
            {missingDocs.map((doc) => (
              <li
                key={doc}
                className="flex items-center gap-3 p-3 bg-white/3 border border-white/10 rounded-lg text-sm text-white/60"
              >
                <span className="h-2 w-2 rounded-full bg-red-500 shrink-0" />
                {DOC_LABELS[doc]}
                <span className="ml-auto text-xs text-white/30">Missing</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Fraud signal note */}
      {riskFlags.some((f) => f.severity === "high") && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-300 text-sm">
          ⚠ This listing has been flagged for high-severity issues. Proceed with caution and verify directly with relevant authorities.
        </div>
      )}
    </div>
  );
}
