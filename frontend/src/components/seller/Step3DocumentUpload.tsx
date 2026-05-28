import { useState } from "react";
import { Upload, CheckCircle2 } from "lucide-react";

interface UploadState {
  ec: File | null;
  sale_deed: File | null;
  photos: File[];
}

interface Step3Props {
  uploads: UploadState;
  onChange: (uploads: UploadState) => void;
}

const DOC_FIELDS: Array<{ key: keyof Omit<UploadState, "photos">; label: string }> = [
  { key: "ec", label: "Encumbrance Certificate (EC)" },
  { key: "sale_deed", label: "Sale Deed" },
];

export default function Step3DocumentUpload({ uploads, onChange }: Step3Props) {
  function handleFile(key: keyof Omit<UploadState, "photos">, file: File | null) {
    onChange({ ...uploads, [key]: file });
  }

  function handlePhotos(files: FileList | null) {
    if (!files) return;
    onChange({ ...uploads, photos: [...uploads.photos, ...Array.from(files)] });
  }

  return (
    <div className="space-y-4">
      {DOC_FIELDS.map(({ key, label }) => (
        <div key={key}>
          <label className="text-xs text-white/50 uppercase tracking-wider mb-1 block">{label}</label>
          <label className="flex items-center gap-3 p-3 bg-white/5 border border-white/10 rounded-lg cursor-pointer hover:bg-white/8 transition-colors">
            {uploads[key] ? (
              <>
                <CheckCircle2 className="h-4 w-4 text-green-400 shrink-0" />
                <span className="text-sm text-white truncate">{uploads[key]?.name}</span>
              </>
            ) : (
              <>
                <Upload className="h-4 w-4 text-white/40 shrink-0" />
                <span className="text-sm text-white/40">Upload PDF, JPG or PNG (max 20MB)</span>
              </>
            )}
            <input
              type="file"
              accept=".pdf,.jpg,.jpeg,.png"
              className="hidden"
              onChange={(e) => handleFile(key, e.target.files?.[0] ?? null)}
            />
          </label>
        </div>
      ))}

      {/* Photos */}
      <div>
        <label className="text-xs text-white/50 uppercase tracking-wider mb-1 block">
          Plot Photos ({uploads.photos.length} selected)
        </label>
        <label className="flex items-center gap-3 p-3 bg-white/5 border border-white/10 rounded-lg cursor-pointer hover:bg-white/8 transition-colors">
          <Upload className="h-4 w-4 text-white/40 shrink-0" />
          <span className="text-sm text-white/40">Add photos (JPG, PNG)</span>
          <input
            type="file"
            accept=".jpg,.jpeg,.png"
            multiple
            className="hidden"
            onChange={(e) => handlePhotos(e.target.files)}
          />
        </label>
        {uploads.photos.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {uploads.photos.map((f, i) => (
              <span key={i} className="px-2 py-0.5 bg-white/5 border border-white/10 rounded text-xs text-white/60 truncate max-w-32">
                {f.name}
              </span>
            ))}
          </div>
        )}
      </div>

      <p className="text-xs text-white/30">
        Documents are analyzed by AI after submission. EC and Sale Deed are required for full verification.
      </p>
    </div>
  );
}
