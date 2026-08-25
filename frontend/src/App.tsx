import { useState, useEffect } from 'react';
import type { ContentItem, BatchGenerationParams } from './types';
import { ControlPanel } from './components/ControlPanel';
import { ContentCard } from './components/ContentCard';
import { Trophy, Command, RefreshCw, Zap } from 'lucide-react';

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
    <div className="min-h-screen bg-[#0d0f17] text-slate-100 pb-20">
      {/* Top Navbar */}
      <header className="border-b border-slate-800/80 bg-[#121622]/90 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center">
              <Trophy className="w-5 h-5 text-indigo-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="font-extrabold text-base text-slate-100 tracking-tight">
                  StapuBox Studio
                </h1>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  AGENT 1.0
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-medium">Instagram Sports Engagement Content Engine</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>Grounded Retrieval Operational</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 space-y-8">
        {/* Editorial Hero Header */}
        <div className="relative rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 p-8 border border-slate-800 shadow-2xl">
          <div className="max-w-3xl space-y-3">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-md bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 text-xs font-semibold">
              <Zap className="w-3.5 h-3.5 text-indigo-400" />
              Content Creator Automation Suite
            </div>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
              Publish Fact-Checked Sports Engagement Content.
            </h2>
            <p className="text-sm text-slate-400 leading-relaxed">
              Generate grounded Quiz stickers, opinion polls, fill-in-the-blanks, and numerical trivia instantly formatted for Instagram Story & Reel native tools.
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

        {/* Batch Output Bar */}
        <div className="flex items-center justify-between pt-4 border-t border-slate-800/80">
          <div className="flex items-center gap-2.5">
            <Command className="w-4 h-4 text-indigo-400" />
            <h3 className="text-base font-bold text-slate-200">
              Output Batch ({items.length} Items)
            </h3>
          </div>

          <button
            onClick={handleGenerateBatch}
            disabled={isLoading}
            className="px-3.5 py-1.5 rounded-lg bg-slate-800/90 hover:bg-slate-700/80 text-slate-300 text-xs font-medium transition-colors flex items-center gap-1.5 disabled:opacity-50 border border-slate-700/50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-indigo-400' : ''}`} />
            <span>Refresh Batch</span>
          </button>
        </div>

        {/* Generated Content Cards Grid */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5].map((idx) => (
              <div key={idx} className="vibe-card rounded-2xl p-6 h-64 animate-pulse flex flex-col justify-between">
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
        )}
      </main>
    </div>
  );
}

export default App;
