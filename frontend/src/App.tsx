import { useState, useEffect } from 'react';
import { Leaf, MessageSquare, FlaskConical, Activity, Globe, BookOpen, Cpu, Shield } from 'lucide-react';
import { ChatPanel } from './components/ChatPanel';
import { AssessmentPanel } from './components/AssessmentPanel';
import { StatusPill } from './components/SharedComponents';
import { api } from './services/api';

type TabId = 'chat' | 'structured';
type ApiStatus = 'checking' | 'online' | 'offline';

const PILLARS = [
  { icon: Activity, label: 'Multi-Metric Reasoning', desc: '5 environmental domains' },
  { icon: BookOpen, label: 'Scientific Grounding', desc: 'RAG + ChromaDB evidence' },
  { icon: Cpu, label: 'Conversational Memory', desc: 'Multi-turn session context' },
  { icon: Shield, label: 'Structured Outputs', desc: 'Traceable reasoning audit' },
];

export default function App() {
  const [tab, setTab] = useState<TabId>('chat');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [apiStatus, setApiStatus] = useState<ApiStatus>('checking');

  useEffect(() => {
    api.health()
      .then(() => setApiStatus('online'))
      .catch(() => setApiStatus('offline'));
  }, []);

  const handleSessionCreated = (id: string) => {
    setSessionId(id);
  };

  const resetSession = () => {
    setSessionId(null);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* ── Header ── */}
      <header className="border-b border-slate-800 bg-slate-950/90 backdrop-blur-sm sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-900/60 border border-emerald-700/50 flex items-center justify-center">
              <Leaf size={16} className="text-emerald-400" />
            </div>
            <div>
              <h1 className="text-sm font-bold text-slate-100 leading-none">Darukaa Environmental Scientist</h1>
              <p className="text-xs text-slate-500 mt-0.5 leading-none">Evidence-backed biodiversity & ecosystem reasoning</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <StatusPill status={apiStatus} />
            {sessionId && (
              <button
                onClick={resetSession}
                className="text-xs text-slate-500 hover:text-slate-300 border border-slate-700 hover:border-slate-600 rounded px-2 py-1 transition-colors"
              >
                New Session
              </button>
            )}
            {sessionId && (
              <span className="hidden sm:inline text-xs text-slate-600 font-mono">
                {sessionId.slice(0, 8)}…
              </span>
            )}
          </div>
        </div>
      </header>

      {/* ── Challenge Pillars Banner ── */}
      <div className="border-b border-slate-800/60 bg-slate-900/30">
        <div className="max-w-7xl mx-auto px-4 py-2">
          <div className="flex gap-6 overflow-x-auto pb-0.5">
            {PILLARS.map(({ icon: Icon, label, desc }) => (
              <div key={label} className="flex items-center gap-2 shrink-0">
                <Icon size={13} className="text-emerald-400 shrink-0" />
                <div>
                  <p className="text-xs font-semibold text-slate-300 whitespace-nowrap">{label}</p>
                  <p className="text-xs text-slate-500 whitespace-nowrap">{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Main layout ── */}
      <div className="flex-1 max-w-7xl w-full mx-auto px-4 py-4 flex flex-col lg:flex-row gap-4 min-h-0">

        {/* ── Left: Branding + Domain info ── */}
        <aside className="hidden lg:flex flex-col gap-4 w-64 shrink-0">
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 space-y-3">
            <div className="flex items-center gap-2 text-emerald-400 mb-1">
              <Globe size={14} />
              <span className="text-xs font-semibold uppercase tracking-wider">Darukaa.Earth</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              An AI environmental scientist powered by a curated scientific knowledge base. Provides multi-metric, evidence-backed recommendations across five ecological domains.
            </p>
            <div className="border-t border-slate-700 pt-3 space-y-2">
              {[
                { label: 'Soil Health', color: 'bg-amber-400' },
                { label: 'Land Use / LULC', color: 'bg-green-400' },
                { label: 'Biodiversity', color: 'bg-teal-400' },
                { label: 'Climate Factors', color: 'bg-blue-400' },
                { label: 'Human Impact', color: 'bg-rose-400' },
              ].map(({ label, color }) => (
                <div key={label} className="flex items-center gap-2">
                  <div className={`w-1.5 h-1.5 rounded-full ${color} shrink-0`} />
                  <span className="text-xs text-slate-300">{label}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">How it works</p>
            <ol className="space-y-2 text-xs text-slate-400">
              <li className="flex items-start gap-2"><span className="text-emerald-400 font-bold shrink-0">1.</span>Describe your land in natural language or run a structured demo scenario.</li>
              <li className="flex items-start gap-2"><span className="text-emerald-400 font-bold shrink-0">2.</span>System extracts environmental variables across 5 domains.</li>
              <li className="flex items-start gap-2"><span className="text-emerald-400 font-bold shrink-0">3.</span>If data is insufficient, targeted clarification questions are asked.</li>
              <li className="flex items-start gap-2"><span className="text-emerald-400 font-bold shrink-0">4.</span>Full multi-metric reasoning produces evidence-backed recommendations.</li>
            </ol>
          </div>
        </aside>

        {/* ── Right: Main Panel ── */}
        <div className="flex-1 flex flex-col min-h-0 min-w-0">
          {/* Tab switcher */}
          <div className="flex gap-1 mb-3 bg-slate-900/50 border border-slate-800 rounded-lg p-1 w-fit">
            <button
              id="tab-chat"
              onClick={() => setTab('chat')}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                tab === 'chat'
                  ? 'bg-emerald-900/60 text-emerald-300 border border-emerald-700/50'
                  : 'text-slate-400 hover:text-slate-300'
              }`}
            >
              <MessageSquare size={14} />
              Conversational
            </button>
            <button
              id="tab-structured"
              onClick={() => setTab('structured')}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                tab === 'structured'
                  ? 'bg-emerald-900/60 text-emerald-300 border border-emerald-700/50'
                  : 'text-slate-400 hover:text-slate-300'
              }`}
            >
              <FlaskConical size={14} />
              Structured Demo
            </button>
          </div>

          {/* Panel */}
          <div className="flex-1 bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden min-h-0 flex flex-col" style={{ height: 'calc(100vh - 220px)' }}>
            {tab === 'chat' ? (
              <ChatPanel sessionId={sessionId} onSessionCreated={handleSessionCreated} />
            ) : (
              <AssessmentPanel sessionId={sessionId} onSessionCreated={handleSessionCreated} />
            )}
          </div>
        </div>
      </div>

      {/* ── Footer ── */}
      <footer className="border-t border-slate-800 px-4 py-3 text-center">
        <p className="text-xs text-slate-600">Darukaa.Earth AI Biodiversity Intelligence · Hackathon Demo · Evidence-backed · Multi-metric · Retrievable Knowledge</p>
      </footer>
    </div>
  );
}
