import type { BatchGenerationParams, RetrievalSourceOption } from '../types';
import { Sparkles, Globe, Database, Layers, Sliders, Hash } from 'lucide-react';

interface ControlPanelProps {
  params: BatchGenerationParams;
  onChange: (params: BatchGenerationParams) => void;
  onGenerate: () => void;
  isLoading: boolean;
  sports: string[];
  difficulties: string[];
  formats: string[];
}

export const ControlPanel = ({
  params,
  onChange,
  onGenerate,
  isLoading,
  sports,
  difficulties,
  formats
}: ControlPanelProps) => {
  const retrievalSources: { id: RetrievalSourceOption; label: string; icon: any; color: string }[] = [
    { id: 'web_search', label: 'Live Web Search', icon: Globe, color: 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10' },
    { id: 'chromadb', label: 'ChromaDB Vector', icon: Database, color: 'text-cyan-400 border-cyan-500/30 bg-cyan-500/10' },
    { id: 'both', label: 'Hybrid (Both)', icon: Layers, color: 'text-indigo-400 border-indigo-500/30 bg-indigo-500/10' },
  ];

  return (
    <div className="bg-[#121622]/90 border border-slate-800/80 rounded-2xl p-6 shadow-2xl backdrop-blur-xl space-y-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sliders className="w-5 h-5 text-indigo-400" />
          <h2 className="text-base font-bold text-slate-100">Generation Parameters</h2>
        </div>
        <span className="text-xs text-slate-400 font-medium">Configure format & retrieval rules</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Sport Selector */}
        <div>
          <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
            Sport Category
          </label>
          <select
            value={params.sport}
            onChange={(e) => onChange({ ...params, sport: e.target.value })}
            className="w-full bg-slate-800/80 border border-slate-700/60 rounded-xl px-3 py-2.5 text-sm text-slate-100 font-medium focus:outline-none focus:border-indigo-500 transition-colors"
          >
            {sports.map((sport) => (
              <option key={sport} value={sport}>
                {sport}
              </option>
            ))}
          </select>
        </div>

        {/* Difficulty Level */}
        <div>
          <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
            Difficulty Level
          </label>
          <select
            value={params.difficulty}
            onChange={(e) => onChange({ ...params, difficulty: e.target.value })}
            className="w-full bg-slate-800/80 border border-slate-700/60 rounded-xl px-3 py-2.5 text-sm text-slate-100 font-medium focus:outline-none focus:border-indigo-500 transition-colors"
          >
            {difficulties.map((diff) => (
              <option key={diff} value={diff}>
                {diff}
              </option>
            ))}
          </select>
        </div>

        {/* Content Format */}
        <div>
          <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
            Format Type
          </label>
          <select
            value={params.content_format}
            onChange={(e) => onChange({ ...params, content_format: e.target.value })}
            className="w-full bg-slate-800/80 border border-slate-700/60 rounded-xl px-3 py-2.5 text-sm text-slate-100 font-medium focus:outline-none focus:border-indigo-500 transition-colors"
          >
            {formats.map((fmt) => (
              <option key={fmt} value={fmt}>
                {fmt}
              </option>
            ))}
          </select>
        </div>

        {/* Batch Quantity Selector */}
        <div>
          <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
            Batch Quantity
          </label>
          <div className="relative flex items-center">
            <select
              value={params.count}
              onChange={(e) => onChange({ ...params, count: parseInt(e.target.value, 10) })}
              className="w-full bg-slate-800/80 border border-slate-700/60 rounded-xl px-3 py-2.5 text-sm text-slate-100 font-medium focus:outline-none focus:border-indigo-500 transition-colors pr-8"
            >
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((num) => (
                <option key={num} value={num}>
                  {num} {num === 1 ? 'Item' : 'Items'}
                </option>
              ))}
            </select>
            <Hash className="w-4 h-4 text-slate-500 absolute right-3 pointer-events-none" />
          </div>
        </div>
      </div>

      {/* Retrieval Source Selection Options: Web Search | ChromaDB | Both (Hybrid) */}
      <div className="pt-2 border-t border-slate-800/60">
        <label className="block text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">
          Retrieval Engine Source
        </label>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {retrievalSources.map((source) => {
            const Icon = source.icon;
            const isSelected = params.retrieval_source === source.id;
            return (
              <button
                key={source.id}
                type="button"
                onClick={() => onChange({ ...params, retrieval_source: source.id })}
                className={`p-3 rounded-xl border font-medium text-xs transition-all flex items-center justify-center gap-2.5 ${
                  isSelected
                    ? `${source.color} ring-1 ring-indigo-500/50 shadow-md`
                    : 'bg-slate-800/40 border-slate-700/40 text-slate-400 hover:border-slate-600 hover:text-slate-200'
                }`}
              >
                <Icon className={`w-4 h-4 ${isSelected ? '' : 'text-slate-500'}`} />
                <span className="font-semibold">{source.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Generate CTA Button */}
      <div className="pt-2 flex justify-end">
        <button
          onClick={onGenerate}
          disabled={isLoading}
          className="w-full sm:w-auto px-7 py-3 rounded-xl bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 hover:from-indigo-500 hover:to-pink-500 text-white font-bold text-sm shadow-xl shadow-indigo-500/20 transition-all transform active:scale-95 disabled:opacity-50 flex items-center justify-center gap-2"
        >
          <Sparkles className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          <span>{isLoading ? 'Agent Synthesizing Content...' : `Generate Batch (${params.count} Items)`}</span>
        </button>
      </div>
    </div>
  );
};
