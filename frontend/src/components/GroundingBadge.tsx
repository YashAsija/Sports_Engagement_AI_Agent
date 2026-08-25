import type { GroundingSource } from '../types';
import { Search, Database, Heart, ShieldCheck, ExternalLink } from 'lucide-react';

interface GroundingBadgeProps {
  grounding: GroundingSource;
}

export const GroundingBadge = ({ grounding }: GroundingBadgeProps) => {
  if (grounding.source_type === 'opinion_based') {
    return (
      <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-purple-500/10 text-purple-400 border border-purple-500/20">
        <Heart className="w-3.5 h-3.5 text-purple-400" />
        <span>Opinion Poll (No Fact Check)</span>
      </div>
    );
  }

  if (grounding.source_type === 'web_search') {
    return (
      <div className="group relative inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
        <Search className="w-3.5 h-3.5 text-emerald-400" />
        <span className="truncate max-w-[180px]">{grounding.citation_title}</span>
        {grounding.url_or_id && (
          <a href={grounding.url_or_id} target="_blank" rel="noopener noreferrer" className="hover:underline flex items-center gap-0.5">
            <ExternalLink className="w-3 h-3 ml-0.5" />
          </a>
        )}
      </div>
    );
  }

  if (grounding.source_type === 'chromadb') {
    return (
      <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
        <Database className="w-3.5 h-3.5 text-cyan-400" />
        <span className="truncate max-w-[180px]">ChromaDB: {grounding.citation_title}</span>
      </div>
    );
  }

  return (
    <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
      <ShieldCheck className="w-3.5 h-3.5 text-blue-400" />
      <span>Verified Sports Archive</span>
    </div>
  );
};
