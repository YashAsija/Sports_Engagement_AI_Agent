import { useState, useEffect } from 'react';
import type { ContentItem, BatchGenerationParams } from './types';
import { ControlPanel } from './components/ControlPanel';
import { ContentCard } from './components/ContentCard';
import { Trophy, Sparkles, RefreshCw, ShieldCheck, Flame } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

export function App() {
  const [params, setParams] = useState<BatchGenerationParams>({
    sport: 'Cricket',
    difficulty: 'Medium',
    content_format: 'Mixed Batch',
    count: 5,
    use_web_search: true,
  });

  const [items, setItems] = useState<ContentItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [regeneratingIds, setRegeneratingIds] = useState<string[]>([]);
  const [sports, setSports] = useState<string[]>(['Cricket', 'Football', 'Tennis', 'Basketball', 'Badminton', 'Formula 1']);
  const [difficulties, setDifficulties] = useState<string[]>(['Easy', 'Medium', 'Hard']);
  const [formats, setFormats] = useState<string[]>(['Mixed Batch', 'MCQ', 'True / False', 'This-or-That Poll', 'Fill in the Blank', 'Guess the Number']);

  // Fetch metadata on mount
  useEffect(() => {
    fetch(`${API_BASE}/api/meta`)
      .then((res) => res.json())
      .then((data) => {
        if (data.sports) setSports(data.sports);
        if (data.difficulties) setDifficulties(data.difficulties);
        if (data.formats) setFormats(data.formats);
      })
      .catch((err) => console.warn('Using default metadata', err));

    // Initial batch trigger
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
          use_web_search: params.use_web_search,
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
    <div className="min-h-screen bg-slate-950 text-slate-100 pb-16">
      {/* Top Navbar */}
      <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-orange-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-orange-500/20">
              <Trophy className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-extrabold text-lg text-white tracking-tight flex items-center gap-2">
                StapuBox Sports AI Agent
                <span className="px-2 py-0.5 text-[10px] uppercase font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 rounded-full">
                  v1.0 Pro
                </span>
              </h1>
              <p className="text-xs text-slate-400">Multi-Format Instagram Sports Content Generator</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold">
              <ShieldCheck className="w-4 h-4" />
              <span>Grounded Retrieval Ready</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 space-y-6">
        {/* Banner Hero */}
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-indigo-900 via-purple-900 to-slate-900 p-6 md:p-8 border border-indigo-500/20 shadow-2xl">
          <div className="relative z-10 max-w-2xl space-y-2">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-xs font-bold">
              <Flame className="w-3.5 h-3.5 text-orange-400" />
              Instagram Story & Post Sticker Generator
            </div>
            <h2 className="text-2xl md:text-3xl font-black text-white tracking-tight">
              Create Engaging Sports Content in Seconds
            </h2>
            <p className="text-sm text-slate-300 leading-relaxed">
              Generates grounded MCQs, True/False challenges, Opinion Polls, Fill-in-the-Blanks, and Guess-the-Number trivia supported by live Web Search & ChromaDB historical records.
            </p>
          </div>
        </div>

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

        {/* Batch Output Header */}
        <div className="flex items-center justify-between pt-4 border-t border-slate-800">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-indigo-400" />
            <h3 className="text-lg font-bold text-white">
              Generated Batch ({items.length} Items)
            </h3>
          </div>

          <button
            onClick={handleGenerateBatch}
            disabled={isLoading}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors flex items-center gap-1.5 disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Regenerate Full Batch</span>
          </button>
        </div>

        {/* Generated Content Cards Grid */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {[1, 2, 3, 4, 5].map((idx) => (
              <div key={idx} className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 h-64 animate-pulse flex flex-col justify-between">
                <div className="space-y-3">
                  <div className="h-4 bg-slate-800 rounded w-1/3"></div>
                  <div className="h-6 bg-slate-800 rounded w-3/4"></div>
                  <div className="h-10 bg-slate-800 rounded w-full"></div>
                </div>
                <div className="h-4 bg-slate-800 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {items.map((item) => (
              <ContentCard
                key={item.id}
                item={item}
                onRegenerate={handleRegenerateItem}
                isRegenerating={regeneratingIds.includes(item.id)}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
