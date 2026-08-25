import { useState } from 'react';
import type { ContentItem } from '../types';
import { GroundingBadge } from './GroundingBadge';
import { RefreshCw, Copy, Check, Eye, Smartphone } from 'lucide-react';

interface ContentCardProps {
  item: ContentItem;
  onRegenerate: (id: string) => void;
  isRegenerating: boolean;
}

export const ContentCard = ({ item, onRegenerate, isRegenerating }: ContentCardProps) => {
  const [showAnswer, setShowAnswer] = useState(false);
  const [activeTab, setActiveTab] = useState<'card' | 'instagram'>('card');
  const [copied, setCopied] = useState(false);

  const formatTextForInstagram = () => {
    let text = `🏆 ${item.sport.toUpperCase()} ENGAGEMENT STICKER\n`;
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
      text += `🔥 Opinion Poll:\n${item.prompt}\n\nOption A: ${item.options?.[0]}\nOption B: ${item.options?.[1]}\n`;
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
    text += `\n#${item.sport.replace(/\s+/g, '')} #${item.sport}Trivia #SportsQuiz #InstagramSticker`;
    return text;
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(formatTextForInstagram());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-slate-900/80 backdrop-blur-md border border-slate-800 rounded-2xl p-5 shadow-xl transition-all duration-300 hover:border-slate-700 hover:shadow-2xl flex flex-col justify-between">
      {/* Header Bar */}
      <div>
        <div className="flex items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              {item.format}
            </span>
            <span className="text-xs text-slate-400 font-medium">
              {item.sport} • {item.difficulty || 'Normal'}
            </span>
          </div>

          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setActiveTab(activeTab === 'card' ? 'instagram' : 'card')}
              className={`p-1.5 rounded-lg text-xs font-medium transition-colors flex items-center gap-1 ${
                activeTab === 'instagram'
                  ? 'bg-gradient-to-r from-pink-500 to-purple-600 text-white'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
              title="Toggle Instagram Sticker Preview"
            >
              <Smartphone className="w-3.5 h-3.5" />
              <span>{activeTab === 'instagram' ? 'Sticker Mode' : 'Card Mode'}</span>
            </button>

            <button
              onClick={() => onRegenerate(item.id)}
              disabled={isRegenerating}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors disabled:opacity-50"
              title="Regenerate this item"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRegenerating ? 'animate-spin text-indigo-400' : ''}`} />
            </button>
          </div>
        </div>

        {/* Card Main View */}
        {activeTab === 'card' ? (
          <div className="space-y-4 my-2">
            {/* MCQ View */}
            {item.format === 'MCQ' && (
              <div>
                <h3 className="text-base font-semibold text-slate-100 mb-3">{item.question}</h3>
                <div className="grid grid-cols-2 gap-2">
                  {item.options?.map((opt, i) => {
                    const isCorrect = opt === item.correct_answer;
                    return (
                      <div
                        key={i}
                        className={`p-2.5 rounded-xl border text-sm transition-all ${
                          showAnswer && isCorrect
                            ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-200 font-semibold'
                            : 'bg-slate-800/60 border-slate-700/50 text-slate-300'
                        }`}
                      >
                        <span className="font-bold text-indigo-400 mr-1.5">{String.fromCharCode(65 + i)}.</span>
                        {opt}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* True / False View */}
            {item.format === 'True / False' && (
              <div>
                <p className="text-base font-semibold text-slate-100 mb-3">"{item.statement}"</p>
                <div className="grid grid-cols-2 gap-3">
                  {['True', 'False'].map((val) => {
                    const isCorrect = val === item.correct_answer;
                    return (
                      <div
                        key={val}
                        className={`p-3 text-center rounded-xl border font-bold text-sm transition-all ${
                          showAnswer && isCorrect
                            ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300'
                            : 'bg-slate-800/60 border-slate-700/50 text-slate-300'
                        }`}
                      >
                        {val}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* This-or-That Poll View */}
            {item.format === 'This-or-That Poll' && (
              <div>
                <h3 className="text-base font-semibold text-slate-100 mb-3">{item.prompt}</h3>
                <div className="grid grid-cols-2 gap-3">
                  {item.options?.map((opt, i) => (
                    <div
                      key={i}
                      className="p-3 text-center rounded-xl bg-gradient-to-r from-purple-900/40 to-indigo-900/40 border border-purple-500/30 font-bold text-sm text-purple-200"
                    >
                      {opt}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Fill in the Blank View */}
            {item.format === 'Fill in the Blank' && (
              <div>
                <p className="text-base font-semibold text-slate-100 mb-3 leading-relaxed">
                  {item.sentence_with_blank}
                </p>
                <div className="grid grid-cols-2 gap-2">
                  {item.options?.map((opt, i) => {
                    const isCorrect = opt === item.correct_answer;
                    return (
                      <div
                        key={i}
                        className={`p-2.5 rounded-xl border text-sm transition-all ${
                          showAnswer && isCorrect
                            ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-200 font-semibold'
                            : 'bg-slate-800/60 border-slate-700/50 text-slate-300'
                        }`}
                      >
                        {opt}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Guess the Number View */}
            {item.format === 'Guess the Number' && (
              <div>
                <h3 className="text-base font-semibold text-slate-100 mb-3">{item.question}</h3>
                <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700 flex items-center justify-between">
                  <span className="text-xs text-slate-400">Target Value:</span>
                  <span className="font-mono text-lg font-bold text-amber-400">
                    {showAnswer ? item.target_number : '???'}
                  </span>
                  <span className="text-xs text-slate-400">Range: {item.accepted_tolerance_range}</span>
                </div>
              </div>
            )}

            {/* Grounding Explanation */}
            <div className="pt-2 border-t border-slate-800">
              <p className="text-xs text-slate-400 leading-normal mb-2">
                <span className="font-semibold text-slate-300">Context: </span>
                {item.explanation}
              </p>
              <GroundingBadge grounding={item.grounding} />
            </div>
          </div>
        ) : (
          /* Instagram Sticker Mock View */
          <div className="my-3 p-4 rounded-2xl bg-gradient-to-br from-pink-600 via-purple-700 to-indigo-800 text-white shadow-inner flex flex-col items-center justify-center text-center space-y-3">
            <div className="uppercase tracking-widest text-[10px] font-extrabold bg-white/20 px-2 py-0.5 rounded-full">
              Instagram Story Sticker
            </div>
            
            <div className="bg-white text-slate-900 rounded-xl p-3 w-full shadow-lg">
              <p className="font-extrabold text-sm mb-2">
                {item.question || item.statement || item.prompt || item.sentence_with_blank}
              </p>

              {item.options && (
                <div className="space-y-1.5 text-xs font-semibold">
                  {item.options.map((opt, idx) => (
                    <div key={idx} className="bg-slate-100 p-2 rounded-lg text-slate-800 flex justify-between">
                      <span>{opt}</span>
                      <span className="text-slate-400 font-normal">Tap to vote</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <p className="text-[11px] text-pink-100 opacity-90">
              Drop directly into Instagram Story via Quiz/Poll stickers.
            </p>
          </div>
        )}
      </div>

      {/* Footer Action Row */}
      <div className="pt-3 border-t border-slate-800 flex items-center justify-between gap-2 mt-2">
        {item.format !== 'This-or-That Poll' ? (
          <button
            onClick={() => setShowAnswer(!showAnswer)}
            className="text-xs font-medium text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
          >
            <Eye className="w-3.5 h-3.5" />
            <span>{showAnswer ? 'Hide Answer' : 'Reveal Answer'}</span>
          </button>
        ) : (
          <div className="text-xs text-purple-400 font-medium">Opinion Poll</div>
        )}

        <button
          onClick={handleCopy}
          className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs transition-colors flex items-center gap-1.5"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-emerald-300" /> : <Copy className="w-3.5 h-3.5" />}
          <span>{copied ? 'Copied Text!' : 'Copy for IG'}</span>
        </button>
      </div>
    </div>
  );
};
