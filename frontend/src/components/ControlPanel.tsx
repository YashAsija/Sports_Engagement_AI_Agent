import type { BatchGenerationParams, RetrievalSourceOption } from '../types';
import { Sparkles, Globe, Database, Layers, Sliders, Hash, Activity } from 'lucide-react';
import { motion } from 'framer-motion';

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
  const retrievalSources: { id: RetrievalSourceOption; label: string; desc: string; icon: any; activeClass: string }[] = [
    { id: 'web_search', label: 'Live Web Search', desc: 'Recent match results & transfers', icon: Globe, activeClass: 'border-emerald-500 bg-emerald-500/10 text-emerald-300' },
    { id: 'chromadb', label: 'ChromaDB Vector', desc: 'Historical sports records & stats', icon: Database, activeClass: 'border-cyan-500 bg-cyan-500/10 text-cyan-300' },
    { id: 'both', label: 'Hybrid (Both)', desc: 'Full dual engine grounding', icon: Layers, activeClass: 'border-indigo-500 bg-indigo-500/10 text-indigo-300' },
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      className="sports-card rounded-2xl p-6 shadow-2xl space-y-6 relative overflow-hidden"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-orange-500/10 border border-orange-500/20 text-orange-400">
            <Sliders className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-100">Generation Controls</h2>
            <p className="text-xs text-slate-400">Tailor AI content output parameters</p>
          </div>
        </div>
        
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700/60 text-xs font-mono text-slate-300">
          <Activity className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
          <span>Agent Ready</span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Sport Selector */}
        <div>
          <label className="block text-xs font-bold text-slate-300 mb-2 uppercase tracking-wider">
            Sport Category
          </label>
          <select
            value={params.sport}
            onChange={(e) => onChange({ ...params, sport: e.target.value })}
            className="w-full bg-slate-900/90 border border-slate-700/80 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 font-semibold focus:outline-none focus:border-orange-500 transition-all"
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
          <label className="block text-xs font-bold text-slate-300 mb-2 uppercase tracking-wider">
            Difficulty Level
          </label>
          <select
            value={params.difficulty}
            onChange={(e) => onChange({ ...params, difficulty: e.target.value })}
            className="w-full bg-slate-900/90 border border-slate-700/80 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 font-semibold focus:outline-none focus:border-orange-500 transition-all"
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
          <label className="block text-xs font-bold text-slate-300 mb-2 uppercase tracking-wider">
            Format Type
          </label>
          <select
            value={params.content_format}
            onChange={(e) => onChange({ ...params, content_format: e.target.value })}
            className="w-full bg-slate-900/90 border border-slate-700/80 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 font-semibold focus:outline-none focus:border-orange-500 transition-all"
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
          <label className="block text-xs font-bold text-slate-300 mb-2 uppercase tracking-wider">
            Batch Quantity
          </label>
          <div className="relative flex items-center">
            <select
              value={params.count}
              onChange={(e) => onChange({ ...params, count: parseInt(e.target.value, 10) })}
              className="w-full bg-slate-900/90 border border-slate-700/80 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 font-semibold focus:outline-none focus:border-orange-500 transition-all pr-8"
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

      {/* Retrieval Source Selection Options */}
      <div className="pt-3 border-t border-slate-800/80">
        <label className="block text-xs font-bold text-slate-300 mb-2.5 uppercase tracking-wider">
          Knowledge Retrieval Engine
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
                className={`p-3.5 rounded-xl border text-left transition-all relative overflow-hidden ${
                  isSelected
                    ? `${source.activeClass} shadow-lg shadow-indigo-500/10`
                    : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                }`}
              >
                <div className="flex items-center gap-2.5 mb-1">
                  <Icon className={`w-4 h-4 ${isSelected ? '' : 'text-slate-500'}`} />
                  <span className="font-bold text-xs">{source.label}</span>
                </div>
                <p className="text-[11px] opacity-80 leading-tight">{source.desc}</p>
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
          className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-gradient-to-r from-orange-500 via-indigo-600 to-purple-600 hover:from-orange-600 hover:to-purple-700 text-white font-extrabold text-sm shadow-xl shadow-orange-500/20 transition-all transform active:scale-95 disabled:opacity-50 flex items-center justify-center gap-2"
        >
          <Sparkles className={`w-4.5 h-4.5 ${isLoading ? 'animate-spin' : ''}`} />
          <span>{isLoading ? 'Agent Synthesizing Content...' : `Generate Batch (${params.count} Items)`}</span>
        </button>
      </div>
    </motion.div>
  );
};
