import { useState, useRef, useEffect } from 'react';
import { Send, HelpCircle, Leaf, MessageSquare } from 'lucide-react';
import { api } from '../services/api';
import type { SystemResponse } from '../services/api';
import type { ChatMessage } from '../types';
import { RecommendationCard, ConditionBadge, Spinner } from './SharedComponents';

interface ChatPanelProps {
  sessionId: string | null;
  onSessionCreated: (id: string) => void;
}

function AssistantBubble({ response }: { response: SystemResponse }) {
  if (response.status === 'needs_clarification') {
    return (
      <div className="space-y-3">
        <div className="flex items-start gap-2 text-sm text-amber-300">
          <HelpCircle size={15} className="mt-0.5 shrink-0" />
          <p className="leading-relaxed">{response.clarification_question}</p>
        </div>
        {response.missing_information && response.missing_information.length > 0 && (
          <div>
            <p className="text-xs text-slate-500 mb-1.5">Additional information needed:</p>
            <div className="flex flex-wrap gap-1.5">
              {response.missing_information.map((m) => (
                <span key={m} className="text-xs px-2 py-0.5 rounded-full border border-amber-700/40 bg-amber-900/20 text-amber-300">
                  {m}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Detected conditions */}
      {response.detected_conditions && response.detected_conditions.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">Detected conditions</p>
          <div className="flex flex-wrap gap-2">
            {response.detected_conditions.map((c) => (
              <ConditionBadge key={c} condition={c} />
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {response.recommendations && response.recommendations.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">
            Recommendations ({response.recommendations.length})
          </p>
          <div className="space-y-2">
            {response.recommendations.map((rec, i) => (
              <RecommendationCard key={i} rec={rec} index={i} />
            ))}
          </div>
        </div>
      )}

      {/* Limitations */}
      {response.limitations && response.limitations.length > 0 && (
        <div className="border border-amber-700/30 rounded-lg p-3 bg-amber-900/10">
          <p className="text-xs font-semibold text-amber-300 mb-1.5">Limitations</p>
          <ul className="space-y-1">
            {response.limitations.map((l, i) => (
              <li key={i} className="text-xs text-amber-200/70">· {l}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

const STARTER_PROMPTS = [
  'My wheat farm has very acidic soil (pH 4.5), heavy pesticide use, and low biodiversity. What should I do?',
  'I have agroforestry land near a forest with good rainfall but deforestation is happening nearby.',
  'Dry, sandy soil with almost no vegetation. Very low rainfall, very hot.',
];

export function ChatPanel({ sessionId, onSessionCreated }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const send = async (text: string) => {
    if (!text.trim() || loading) return;
    setError(null);
    setInput('');

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: text.trim(),
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const response = await api.chat({
        message: text.trim(),
        session_id: sessionId ?? undefined,
      });

      if (!sessionId) onSessionCreated(response.session_id);

      const assistantMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: response.clarification_question ?? 'Assessment complete.',
        timestamp: new Date(),
        response,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unexpected error');
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send(input);
    }
  };

  const isEmpty = messages.length === 0;

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
        {isEmpty ? (
          <div className="h-full flex flex-col items-center justify-center text-center px-6 py-10 gap-6">
            <div className="w-14 h-14 rounded-2xl bg-emerald-900/40 border border-emerald-700/50 flex items-center justify-center">
              <Leaf size={26} className="text-emerald-400" />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-200 mb-1">Describe your land in natural language</p>
              <p className="text-xs text-slate-500 max-w-xs">The system will ask clarifying questions until it has enough data for a full multi-metric assessment.</p>
            </div>
            <div className="w-full max-w-sm space-y-2">
              {STARTER_PROMPTS.map((p) => (
                <button
                  key={p}
                  onClick={() => send(p)}
                  className="w-full text-left text-xs text-slate-300 bg-slate-800/60 border border-slate-700 hover:border-emerald-700/50 hover:bg-slate-800 rounded-lg px-3 py-2.5 transition-colors"
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] rounded-xl px-4 py-3 ${msg.role === 'user' ? 'bg-emerald-900/50 border border-emerald-700/40 text-sm text-slate-100' : 'bg-slate-800/80 border border-slate-700 w-full max-w-full'}`}>
                {msg.role === 'user' ? (
                  <p className="text-sm leading-relaxed">{msg.content}</p>
                ) : msg.response ? (
                  <div>
                    <div className="flex items-center gap-2 mb-3 pb-2 border-b border-slate-700/50">
                      <MessageSquare size={13} className="text-emerald-400" />
                      <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">
                        {msg.response.status === 'complete' ? 'Assessment Complete' : 'Clarification Needed'}
                      </span>
                    </div>
                    <AssistantBubble response={msg.response} />
                  </div>
                ) : null}
              </div>
            </div>
          ))
        )}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-800/80 border border-slate-700 rounded-xl px-4 py-3 flex items-center gap-2">
              <Spinner size={14} />
              <span className="text-xs text-slate-400">Analysing environmental profile…</span>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-900/30 border border-red-700/40 rounded-lg px-4 py-2 text-xs text-red-300">
            Error: {error}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-slate-700/50 p-3">
        <div className="flex gap-2 items-end">
          <textarea
            ref={inputRef}
            rows={2}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Describe your farm, forest, or land ecosystem…"
            className="flex-1 bg-slate-800/60 border border-slate-700 text-slate-100 text-sm rounded-lg px-3 py-2 resize-none focus:outline-none focus:border-emerald-600 placeholder-slate-500 min-h-[56px]"
          />
          <button
            onClick={() => send(input)}
            disabled={!input.trim() || loading}
            id="chat-send-btn"
            className="bg-emerald-700 hover:bg-emerald-600 disabled:bg-slate-700 disabled:text-slate-500 text-white rounded-lg p-3 transition-colors flex items-center justify-center shrink-0"
          >
            {loading ? <Spinner size={16} /> : <Send size={16} />}
          </button>
        </div>
        <p className="text-xs text-slate-600 mt-1.5 pl-1">Enter ↵ to send · Shift+Enter for new line</p>
      </div>
    </div>
  );
}
