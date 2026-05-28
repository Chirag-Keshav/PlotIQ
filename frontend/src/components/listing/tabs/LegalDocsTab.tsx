import { FileText, CheckCircle2, Clock, XCircle, Upload } from "lucide-react";
import DisclaimerBanner from "../../ui/DisclaimerBanner";

interface Document {
  id: string;
  doc_type: string;
  analysis_status: string;
  ai_analysis?: {
    named_parties?: string[];
    survey_numbers?: string[];
    risk_clauses?: string[];
    missing_approvals?: string[];
    summary?: string;
  };
  uploaded_at: string;
}

interface LegalDocsTabProps {
  documents: Document[];
}

const DOC_TYPES = [
  { key: "ec", label: "Encumbrance Certificate (EC)" },
  { key: "sale_deed", label: "Sale Deed" },
  { key: "layout_approval", label: "Layout Approval" },
  { key: "mutation_register", label: "Mutation Register" },
  { key: "patta", label: "Patta / ROR" },
];

function StatusIcon({ status }: { status: string }) {
  if (status === "complete") return <CheckCircle2 className="h-4 w-4 text-green-400" />;
  if (status === "processing") return <Clock className="h-4 w-4 text-yellow-400 animate-spin" />;
  if (status === "failed") return <XCircle className="h-4 w-4 text-red-400" />;
  return <Clock className="h-4 w-4 text-white/30" />;
}

export default function LegalDocsTab({ documents }: LegalDocsTabProps) {
  const docsByType = Object.fromEntries(
    documents.map((d) => [d.doc_type, d])
  );

  return (
    <div className="space-y-6">
      <DisclaimerBanner variant="document" />

      {/* Upload status tracker */}
      <div className="space-y-2">
        <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider">Document Status</h3>
        {DOC_TYPES.map(({ key, label }) => {
          const doc = docsByType[key];
          return (
            <div key={key} className="flex items-center gap-3 p-3 bg-white/3 border border-white/10 rounded-lg">
              <FileText className="h-4 w-4 text-white/40 shrink-0" />
              <span className="flex-1 text-sm text-white">{label}</span>
              {doc ? (
                <StatusIcon status={doc.analysis_status} />
              ) : (
                <span className="flex items-center gap-1 text-xs text-white/30">
                  <Upload className="h-3 w-3" /> Not uploaded
                </span>
              )}
            </div>
          );
        })}
      </div>

      {/* AI summaries per uploaded doc */}
      {documents.filter((d) => d.analysis_status === "complete" && d.ai_analysis).map((doc) => (
        <div key={doc.id} className="p-4 bg-white/3 border border-white/10 rounded-xl space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-semibold text-white capitalize">
              {doc.doc_type.replace(/_/g, " ")} — AI Analysis
            </h4>
            <span className="text-xs text-white/30">
              {new Date(doc.uploaded_at).toLocaleDateString()}
            </span>
          </div>

          {doc.ai_analysis?.summary && (
            <p className="text-sm text-white/70">{doc.ai_analysis.summary}</p>
          )}

          {doc.ai_analysis?.named_parties && doc.ai_analysis.named_parties.length > 0 && (
            <div>
              <p className="text-xs text-white/40 mb-1">Parties</p>
              <div className="flex flex-wrap gap-1">
                {doc.ai_analysis.named_parties.map((p, i) => (
                  <span key={i} className="px-2 py-0.5 bg-white/5 border border-white/10 rounded text-xs text-white/70">{p}</span>
                ))}
              </div>
            </div>
          )}

          {doc.ai_analysis?.risk_clauses && doc.ai_analysis.risk_clauses.length > 0 && (
            <div>
              <p className="text-xs text-red-400/70 mb-1">Risk Clauses</p>
              <ul className="space-y-1">
                {doc.ai_analysis.risk_clauses.map((c, i) => (
                  <li key={i} className="text-xs text-red-300/70 pl-2 border-l border-red-500/30">{c}</li>
                ))}
              </ul>
            </div>
          )}

          {doc.ai_analysis?.missing_approvals && doc.ai_analysis.missing_approvals.length > 0 && (
            <div>
              <p className="text-xs text-yellow-400/70 mb-1">Missing Approvals</p>
              <ul className="space-y-1">
                {doc.ai_analysis.missing_approvals.map((m, i) => (
                  <li key={i} className="text-xs text-yellow-300/70 pl-2 border-l border-yellow-500/30">{m}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ))}

      {documents.length === 0 && (
        <div className="text-center py-8 text-white/30 text-sm">
          No documents uploaded yet.
        </div>
      )}
    </div>
  );
}
