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

interface Step2Props {
  details: PlotDetails;
  onChange: (field: keyof PlotDetails, value: string) => void;
}

const LOCALITIES = [
  "Kokapet", "Shadnagar", "Adibatla", "Patancheru",
  "Ibrahimpatnam", "Shamshabad", "Ghatkesar", "Sangareddy",
];

const USE_TYPES = ["residential", "commercial", "agricultural"];
const ROAD_ACCESS = ["40ft", "60ft", "100ft", "highway", "none"];
const OWNERSHIP = ["individual", "joint", "company"];

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="text-xs text-white/50 uppercase tracking-wider mb-1 block">{label}</label>
      {children}
    </div>
  );
}

function SelectInput({
  value,
  onChange,
  options,
}: {
  value: string;
  onChange: (v: string) => void;
  options: string[];
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white text-sm focus:outline-none focus:border-white/30 appearance-none"
    >
      <option value="">Select...</option>
      {options.map((o) => (
        <option key={o} value={o} className="bg-black capitalize">
          {o}
        </option>
      ))}
    </select>
  );
}

export default function Step2PlotDetails({ details, onChange }: Step2Props) {
  function input(field: keyof PlotDetails) {
    return (
      <input
        type="text"
        value={details[field]}
        onChange={(e) => onChange(field, e.target.value)}
        className="w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white text-sm placeholder-white/20 focus:outline-none focus:border-white/30"
      />
    );
  }

  return (
    <div className="space-y-4">
      <Field label="Title">{input("title")}</Field>
      <Field label="Description">
        <textarea
          value={details.description}
          onChange={(e) => onChange("description", e.target.value)}
          rows={3}
          className="w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white text-sm placeholder-white/20 focus:outline-none focus:border-white/30 resize-none"
        />
      </Field>
      <div className="grid grid-cols-2 gap-3">
        <Field label="Price (Lakhs)">{input("price_lakhs")}</Field>
        <Field label="Area (sqyd)">{input("area_sqyd")}</Field>
      </div>
      <Field label="Locality">
        <SelectInput value={details.locality} onChange={(v) => onChange("locality", v)} options={LOCALITIES} />
      </Field>
      <Field label="Use Type">
        <SelectInput value={details.use_type} onChange={(v) => onChange("use_type", v)} options={USE_TYPES} />
      </Field>
      <Field label="Road Access">
        <SelectInput value={details.road_access} onChange={(v) => onChange("road_access", v)} options={ROAD_ACCESS} />
      </Field>
      <Field label="Ownership Type">
        <SelectInput value={details.ownership_type} onChange={(v) => onChange("ownership_type", v)} options={OWNERSHIP} />
      </Field>
    </div>
  );
}
