export default function SkeletonCard() {
  return (
    <div className="glass-card p-4 animate-pulse">
      <div className="flex justify-between items-start mb-2">
        <div className="h-4 bg-white/10 rounded w-3/4" />
        <div className="h-5 bg-white/10 rounded w-10" />
      </div>
      <div className="h-3 bg-white/5 rounded w-1/2 mb-3" />
      <div className="flex justify-between items-center">
        <div className="h-6 bg-white/10 rounded w-20" />
        <div className="flex gap-1">
          <div className="h-4 bg-white/5 rounded w-16" />
          <div className="h-4 bg-white/5 rounded w-16" />
        </div>
      </div>
      <div className="mt-3 h-8 bg-white/5 rounded-lg" />
    </div>
  );
}
