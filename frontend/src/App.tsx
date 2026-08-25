import { useState, useEffect } from 'react';
import type { ContentItem, BatchGenerationParams } from './types';
import { ControlPanel } from './components/ControlPanel';
import { ContentCard } from './components/ContentCard';
import { Trophy, Command, RefreshCw, Flame, Sparkles, Layers, Activity } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = 'http://localhost:8000';

export function App() {
  const [params, setParams] = useState<BatchGenerationParams>({
    sport: 'Cricket',
    difficulty: 'Medium',
    content_format: 'Mixed Batch',
    count: 5,
    retrieval_source: 'both',
  });

  const [items, setItems] = useState<ContentItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [regeneratingIds, setRegeneratingIds] = useState<string[]>([]);
  const [sports, setSports] = useState<string[]>(['Cricket', 'Football', 'Tennis', 'Basketball', 'Badminton', 'Formula 1']);
  const [difficulties, setDifficulties] = useState<string[]>(['Easy', 'Medium', 'Hard']);
  const [formats, setFormats] = useState<string[]>(['Mixed Batch', 'MCQ', 'True / False', 'This-or-That Poll', 'Fill in the Blank', 'Guess the Number']);

  useEffect(() => {
    fetch(`${API_BASE}/api/meta`)
      .then((res) => res.json())
      .then((data) => {
        if (data.sports) setSports(data.sports);
        if (data.difficulties) setDifficulties(data.difficulties);
        if (data.formats) setFormats(data.formats);
      })
      .catch((err) => console.warn('Using default metadata', err));

    handleGenerateBatch();
  }, []);

  const handleGenerateBatch = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/generate-batch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      });
      const data = await res.json();
      if (data.items) {
        setItems(data.items);
      }
    } catch (err) {
      console.error('Batch generation error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegenerateItem = async (targetId: string) => {
    setRegeneratingIds((prev) => [...prev, targetId]);
    const targetItem = items.find((it) => it.id === targetId);
    try {
      const res = await fetch(`${API_BASE}/api/regenerate-item`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sport: params.sport,
          difficulty: params.difficulty,
          content_format: targetItem ? targetItem.format : 'MCQ',
          target_item_id: targetId,
          retrieval_source: params.retrieval_source,
        }),
      });
      const data = await res.json();
      if (data.item) {
        setItems((prev) => prev.map((it) => (it.id === targetId ? data.item : it)));
      }
    } catch (err) {
      console.error('Regenerate item error:', err);
    } finally {
      setRegeneratingIds((prev) => prev.filter((id) => id !== targetId));
    }
  };

  return (
    <div className="min-h-screen stadium-bg text-slate-100 pb-24 selection:bg-orange-500 selection:text-white">
      {/* Navbar Header */}
      <header className="border-b border-slate-800/80 bg-[#07090e]/90 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-orange-500 to-indigo-600 p-0.5 shadow-lg shadow-orange-500/20">
              <div className="w-full h-full bg-[#07090e] rounded-[10px] flex items-center justify-center">
                <Trophy className="w-5 h-5 text-orange-400" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="font-black text-base text-white tracking-tight">
                  StapuBox Sports AI
                </h1>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-orange-500/10 text-orange-400 border border-orange-500/20">
                  STUDIO v1.0
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-medium">Multi-Format Instagram Content Agent</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>RAG Engine Ready</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 space-y-8">
        {/* Creative Sports Hero Banner */}
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative rounded-3xl bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 p-8 sm:p-10 border border-slate-800 shadow-2xl overflow-hidden"
        >
          <div className="absolute -right-12 -top-12 w-64 h-64 bg-orange-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute -left-12 -bottom-12 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

          <div className="relative z-10 max-w-3xl space-y-4">
            <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-orange-500/10 text-orange-400 border border-orange-500/20 text-xs font-bold uppercase tracking-wider">
              <Flame className="w-3.5 h-3.5 text-orange-400" />
              Interactive Instagram Story & Sticker Engine
            </div>
            
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-black text-white tracking-tight leading-none">
              Generate High-Converting Sports Content.
            </h2>
            
            <p className="text-sm sm:text-base text-slate-300 leading-relaxed font-medium">
              Create fact-checked MCQs, opinion polls, true/false challenges, and numerical trivia powered by live web search & ChromaDB vector store.
            </p>
          </div>
        </motion.div>

        {/* Control Panel */}
        <ControlPanel
          params={params}
          onChange={setParams}
          onGenerate={handleGenerateBatch}
          isLoading={isLoading}
          sports={sports}
          difficulties={difficulties}
          formats={formats}
        />

        {/* Output Header Bar */}
        <div className="flex items-center justify-between pt-6 border-t border-slate-800/80">
          <div className="flex items-center gap-2.5">
            <Sparkles className="w-5 h-5 text-orange-400" />
            <h3 className="text-lg font-bold text-white tracking-tight">
              Generated Engagement Cards ({items.length} Items)
            </h3>
          </div>

          <button
            onClick={handleGenerateBatch}
            disabled={isLoading}
            className="px-4 py-2 rounded-xl bg-slate-800/90 hover:bg-slate-700 text-slate-200 text-xs font-bold transition-all flex items-center gap-2 disabled:opacity-50 border border-slate-700/60 shadow-md"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-orange-400' : ''}`} />
            <span>Regenerate Full Batch</span>
          </button>
        </div>

        {/* Animated Cards Grid */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Array.from({ length: params.count }).map((_, idx) => (
              <div key={idx} className="sports-card rounded-2xl p-6 h-64 animate-pulse flex flex-col justify-between">
                <div className="space-y-4">
                  <div className="h-4 bg-slate-800/80 rounded w-1/3"></div>
                  <div className="h-6 bg-slate-800/80 rounded w-3/4"></div>
                  <div className="h-10 bg-slate-800/80 rounded w-full"></div>
                </div>
                <div className="h-4 bg-slate-800/80 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        ) : (
          <AnimatePresence>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {items.map((item) => (
                <ContentCard
                  key={item.id}
                  item={item}
                  onRegenerate={handleRegenerateItem}
                  isRegenerating={regeneratingIds.includes(item.id)}
                />
              ))}
            </div>
          </AnimatePresence>
        )}
      </main>
    </div>
  );
}

export default App;
