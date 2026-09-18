import React from 'react';

export default function SkeletonCard() {
  return (
    <div className="rounded-2xl border border-slate-200/80 bg-white p-4 shadow-sm animate-pulse space-y-3">
      <div className="flex justify-between items-center">
        <div className="h-4 bg-slate-200 rounded w-24" />
        <div className="h-4 bg-slate-200 rounded w-16" />
      </div>
      <div className="h-5 bg-slate-200 rounded w-3/4" />
      <div className="flex gap-2">
        <div className="h-3 bg-slate-200 rounded w-16" />
        <div className="h-3 bg-slate-200 rounded w-20" />
      </div>
    </div>
  );
}
