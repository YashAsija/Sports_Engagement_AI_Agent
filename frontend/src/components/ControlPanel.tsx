import type { BatchGenerationParams } from '../types';
import { Sparkles, Globe, Database, Sliders, Hash } from 'lucide-react';

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
  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-2xl backdrop-blur-lg">
      <div className="flex items-center gap-2 mb-4">
        <Sliders className="w-5 h-5 text-indigo-400" />
        <h2 className="text-lg font-bold text-slate-100">Generation Controls</h2>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-4">
        {/* Sport Selector */}
        <div>
          <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
            Sport Category
          </label>
          <select
            value={params.sport}
            onChange={(e) => onChange({ ...params, sport: e.target.value })}
            className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-slate-100 font-medium focus:outline-none focus:border-indigo-500 transition-colors"
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
            className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-slate-100 font-medium focus:outline-none focus:border-indigo-500 transition-colors"
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
            className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-slate-100 font-medium focus:outline-none focus:border-indigo-500 transition-colors"
          >
            {formats.map((fmt) => (
              <option key={fmt} value={fmt}>
                {fmt}
              </option>
            ))}
          </select>
        </div>

        {/* Batch Item Count Selector */}
        <div>
          <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
            Batch Quantity
          </label>
          <div className="relative flex items-center">
            <select
              value={params.count}
              onChange={(e) => onChange({ ...params, count: parseInt(e.target.value, 10) })}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-slate-100 font-medium focus:outline-none focus:border-indigo-500 transition-colors"
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

        {/* Retrieval Mode Toggle */}
        <div>
          <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
            Retrieval Source
          </label>
          <button
            onClick={() => onChange({ ...params, use_web_search: !params.use_web_search })}
            className={`w-full py-2.5 px-3 rounded-xl border font-medium text-sm transition-all flex items-center justify-center gap-2 ${
              params.use_web_search
                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                : 'bg-cyan-500/10 border-cyan-500/30 text-cyan-300'
            }`}
          >
            {params.use_web_search ? (
              <>
                <Globe className="w-4 h-4 text-emerald-400" />
                <span className="truncate">Web Search</span>
              </>
            ) : (
              <>
                <Database className="w-4 h-4 text-cyan-400" />
                <span className="truncate">ChromaDB</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Generate Action Button */}
      <div className="mt-5 flex justify-end">
        <button
          onClick={onGenerate}
          disabled={isLoading}
          className="w-full sm:w-auto px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 hover:from-indigo-500 hover:to-pink-500 text-white font-bold text-sm shadow-lg shadow-indigo-500/25 transition-all transform active:scale-95 disabled:opacity-50 flex items-center justify-center gap-2"
        >
          <Sparkles className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          <span>{isLoading ? 'Agent Synthesizing Content...' : `Generate Batch (${params.count} Items)`}</span>
        </button>
      </div>
    </div>
  );
};
