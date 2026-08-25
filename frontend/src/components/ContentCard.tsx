import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { ContentItem } from '../types';
import { GroundingBadge } from './GroundingBadge';
import { RefreshCw, Copy, Check, Eye, Smartphone, CheckCircle2, ExternalLink } from 'lucide-react';
import confetti from 'canvas-confetti';

interface ContentCardProps {
  item: ContentItem;
  onRegenerate: (id: string) => void;
  isRegenerating: boolean;
}

export const ContentCard = ({ item, onRegenerate, isRegenerating }: ContentCardProps) => {
  const [showAnswer, setShowAnswer] = useState(false);
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'card' | 'instagram'>('card');
  const [copied, setCopied] = useState(false);

  const formatTextForInstagram = () => {
    let text = `🏆 STAPUBOX SPORTS STICKER • ${item.sport.toUpperCase()}\n`;
    text += `Format: ${item.format}\n\n`;

    if (item.format === 'MCQ') {
      text += `❓ Quiz Question:\n${item.question}\n\nOptions:\n`;
      item.options?.forEach((opt, idx) => {
        const char = String.fromCharCode(65 + idx);
        text += `${char}) ${opt}\n`;
      });
      text += `\n✅ Correct Answer: ${item.correct_answer}\n`;
    } else if (item.format === 'True / False') {
      text += `⚡ True or False Challenge:\n${item.statement}\n\n`;
      text += `✅ Correct Answer: ${item.correct_answer}\n`;
    } else if (item.format === 'This-or-That Poll') {
      text += `🔥 Community Debate:\n${item.prompt}\n\nOption A: ${item.options?.[0]}\nOption B: ${item.options?.[1]}\n`;
    } else if (item.format === 'Fill in the Blank') {
      text += `✏️ Fill in the Blank:\n${item.sentence_with_blank}\n\nOptions:\n`;
      item.options?.forEach((opt) => {
        text += `• ${opt}\n`;
      });
      text += `\n✅ Answer: ${item.correct_answer}\n`;
    } else if (item.format === 'Guess the Number') {
      text += `🎯 Guess the Number:\n${item.question}\n\nTarget Number: ${item.target_number}\nTolerance Range: ${item.accepted_tolerance_range}\n`;
    }

    text += `\n📌 Context: ${item.explanation}\n`;
    if (item.grounding?.url_or_id) {
      text += `🔗 Source: ${item.grounding.url_or_id}\n`;
    }
    text += `\n#${item.sport.replace(/\s+/g, '')} #SportsTrivia #InstagramStickers #StapuBoxStudio`;
    return text;
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(formatTextForInstagram());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleOptionClick = (opt: string) => {
    setSelectedOption(opt);
    setShowAnswer(true);

    if (opt === item.correct_answer) {
      confetti({
        particleCount: 50,
        spread: 60,
        origin: { y: 0.8 },
        colors: ['#f97316', '#6366f1', '#10b981']
      });
    }
  };

  const getFormatBadgeColor = (fmt: string) => {
    switch (fmt) {
      case 'MCQ': return 'bg-orange-500/10 text-orange-400 border-orange-500/30';
      case 'True / False': return 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30';
      case 'This-or-That Poll': return 'bg-purple-500/10 text-purple-400 border-purple-500/30';
      case 'Fill in the Blank': return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      default: return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.3 }}
      className="sports-card rounded-2xl p-6 flex flex-col justify-between relative overflow-hidden group"
    >
      {/* Top Card Header */}
      <div>
        <div className="flex items-center justify-between gap-2 mb-4">
          <div className="flex items-center gap-2">
            <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getFormatBadgeColor(item.format)}`}>
              {item.format}
            </span>
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">
              {item.sport} • {item.difficulty || 'Normal'}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveTab(activeTab === 'card' ? 'instagram' : 'card')}
              className={`px-2.5 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 border ${
                activeTab === 'instagram'
                  ? 'bg-gradient-to-r from-pink-500 to-purple-600 border-pink-400 text-white shadow-md'
                  : 'bg-slate-800/80 border-slate-700/60 text-slate-300 hover:bg-slate-700'
              }`}
            >
              <Smartphone className="w-3.5 h-3.5" />
              <span>{activeTab === 'instagram' ? 'Sticker View' : 'Card View'}</span>
            </button>

            <button
              onClick={() => onRegenerate(item.id)}
              disabled={isRegenerating}
              className="p-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-slate-300 hover:bg-slate-700 hover:text-white transition-all disabled:opacity-50"
              title="Regenerate single item"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRegenerating ? 'animate-spin text-orange-400' : ''}`} />
            </button>
          </div>
        </div>

        {/* Card Main View */}
        <AnimatePresence mode="wait">
          {activeTab === 'card' ? (
            <motion.div
              key="card-view"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-4 my-2"
            >
              {/* MCQ View */}
              {item.format === 'MCQ' && (
                <div>
                  <h3 className="text-base font-bold text-slate-100 mb-4 leading-snug">{item.question}</h3>
                  <div className="grid grid-cols-2 gap-2.5">
                    {item.options?.map((opt, i) => {
                      const isCorrect = opt === item.correct_answer;
                      const isSelected = opt === selectedOption;
                      return (
                        <button
                          key={i}
                          onClick={() => handleOptionClick(opt)}
                          className={`p-3 rounded-xl border text-sm text-left transition-all font-medium flex items-center justify-between ${
                            showAnswer && isCorrect
                              ? 'bg-emerald-500/20 border-emerald-500 text-emerald-200 font-bold shadow-lg shadow-emerald-500/10'
                              : showAnswer && isSelected && !isCorrect
                              ? 'bg-red-500/20 border-red-500/60 text-red-200'
                              : 'bg-slate-800/60 border-slate-700/60 text-slate-200 hover:bg-slate-800 hover:border-slate-600'
                          }`}
                        >
                          <span>
                            <span className="font-mono text-orange-400 font-bold mr-2">{String.fromCharCode(65 + i)}.</span>
                            {opt}
                          </span>
                          {showAnswer && isCorrect && <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />}
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* True / False View */}
              {item.format === 'True / False' && (
                <div>
                  <p className="text-base font-bold text-slate-100 mb-4 leading-relaxed italic">"{item.statement}"</p>
                  <div className="grid grid-cols-2 gap-3">
                    {['True', 'False'].map((val) => {
                      const isCorrect = val === item.correct_answer;
                      const isSelected = val === selectedOption;
                      return (
                        <button
                          key={val}
                          onClick={() => handleOptionClick(val)}
                          className={`p-3.5 text-center rounded-xl border font-extrabold text-sm transition-all ${
                            showAnswer && isCorrect
                              ? 'bg-emerald-500/20 border-emerald-500 text-emerald-300 shadow-lg shadow-emerald-500/10'
                              : showAnswer && isSelected && !isCorrect
                              ? 'bg-red-500/20 border-red-500/60 text-red-300'
                              : 'bg-slate-800/60 border-slate-700/60 text-slate-200 hover:bg-slate-800'
                          }`}
                        >
                          {val}
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* This-or-That Poll View */}
              {item.format === 'This-or-That Poll' && (
                <div>
                  <h3 className="text-base font-bold text-slate-100 mb-4">{item.prompt}</h3>
                  <div className="grid grid-cols-2 gap-3">
                    {item.options?.map((opt, i) => (
                      <button
                        key={i}
                        onClick={() => setSelectedOption(opt)}
                        className={`p-3.5 text-center rounded-xl border font-bold text-sm transition-all ${
                          selectedOption === opt
                            ? 'bg-gradient-to-r from-purple-600 to-indigo-600 border-purple-400 text-white shadow-lg'
                            : 'bg-gradient-to-r from-purple-950/40 to-indigo-950/40 border-purple-500/30 text-purple-200 hover:border-purple-400'
                        }`}
                      >
                        {opt}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Fill in the Blank View */}
              {item.format === 'Fill in the Blank' && (
                <div>
                  <p className="text-base font-bold text-slate-100 mb-4 leading-relaxed">
                    {item.sentence_with_blank}
                  </p>
                  <div className="grid grid-cols-2 gap-2.5">
                    {item.options?.map((opt, i) => {
                      const isCorrect = opt === item.correct_answer;
                      return (
                        <button
                          key={i}
                          onClick={() => handleOptionClick(opt)}
                          className={`p-3 rounded-xl border text-sm text-left font-medium transition-all ${
                            showAnswer && isCorrect
                              ? 'bg-emerald-500/20 border-emerald-500 text-emerald-200 font-bold'
                              : 'bg-slate-800/60 border-slate-700/60 text-slate-200 hover:bg-slate-800'
                          }`}
                        >
                          {opt}
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Guess the Number View */}
              {item.format === 'Guess the Number' && (
                <div>
                  <h3 className="text-base font-bold text-slate-100 mb-4">{item.question}</h3>
                  <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/70 flex items-center justify-between">
                    <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Target Value:</span>
                    <span className="font-mono text-xl font-extrabold text-orange-400">
                      {showAnswer ? item.target_number : '???'}
                    </span>
                    <span className="text-xs text-slate-400 font-medium">Range: {item.accepted_tolerance_range}</span>
                  </div>
                </div>
              )}

              {/* Context Grounding Section with explicit Source URL footer */}
              <div className="pt-3 border-t border-slate-800/80 space-y-2">
                <p className="text-xs text-slate-400 leading-normal">
                  <span className="font-bold text-slate-300">Context: </span>
                  {item.explanation}
                </p>
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <GroundingBadge grounding={item.grounding} />
                  {item.grounding?.url_or_id && (
                    <div className="text-[11px] font-mono text-slate-400 flex items-center gap-1">
                      <span>Source:</span>
                      {item.grounding.url_or_id.startsWith('http') ? (
                        <a href={item.grounding.url_or_id} target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:underline truncate max-w-[150px] inline-flex items-center gap-0.5">
                          <span>{item.grounding.url_or_id.replace(/^https?:\/\//, '')}</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      ) : (
                        <span className="text-slate-300 font-semibold">{item.grounding.url_or_id}</span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          ) : (
            /* Instagram Native Sticker Canvas Mock */
            <motion.div
              key="instagram-view"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="my-3 p-5 rounded-2xl bg-gradient-to-br from-pink-600 via-purple-700 to-indigo-800 text-white shadow-2xl flex flex-col items-center justify-center text-center space-y-4 relative"
            >
              <div className="inline-flex items-center gap-1.5 text-[10px] font-extrabold uppercase tracking-widest bg-white/20 backdrop-blur-md px-3 py-1 rounded-full border border-white/20">
                <Smartphone className="w-3 h-3" />
                <span>Instagram Story Sticker Preview</span>
              </div>

              <div className="bg-white text-slate-900 rounded-xl p-4 w-full shadow-2xl text-left border border-white/50">
                <p className="font-black text-sm mb-3 text-slate-900">
                  {item.question || item.statement || item.prompt || item.sentence_with_blank}
                </p>

                {item.options && (
                  <div className="space-y-2 text-xs font-bold">
                    {item.options.map((opt, idx) => (
                      <div key={idx} className="bg-slate-100 p-2.5 rounded-lg text-slate-800 flex items-center justify-between border border-slate-200">
                        <span>{opt}</span>
                        <span className="text-[10px] text-slate-400 font-medium uppercase">Tap sticker</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <p className="text-[11px] text-pink-100 font-medium opacity-95">
                Drop directly into native Instagram text/sticker tools.
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Card Footer Actions */}
      <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between gap-2 mt-3">
        {item.format !== 'This-or-That Poll' ? (
          <button
            onClick={() => setShowAnswer(!showAnswer)}
            className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors flex items-center gap-1.5"
          >
            <Eye className="w-3.5 h-3.5" />
            <span>{showAnswer ? 'Hide Answer' : 'Reveal Answer'}</span>
          </button>
        ) : (
          <div className="text-xs text-purple-400 font-bold uppercase tracking-wider">Opinion Poll</div>
        )}

        <button
          onClick={handleCopy}
          className="px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs transition-all shadow-md shadow-indigo-600/20 flex items-center gap-1.5 active:scale-95"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-emerald-300" /> : <Copy className="w-3.5 h-3.5" />}
          <span>{copied ? 'Copied to Clipboard!' : 'Copy for Instagram'}</span>
        </button>
      </div>
    </motion.div>
  );
};
