import { useState } from 'react';
import { FlaskConical, Play, ChevronDown, ChevronUp } from 'lucide-react';
import { api } from '../services/api';
import type { SystemResponse } from '../services/api';
import { DEMO_SCENARIOS } from '../types';
import { RecommendationCard, ReasoningTrace, ConditionBadge, Spinner, EvidenceCard } from './SharedComponents';

interface AssessmentPanelProps {
  sessionId: string | null;
  onSessionCreated: (id: string) => void;
}

export function AssessmentPanel({ sessionId, onSessionCreated }: AssessmentPanelProps) {
  const [activeScenario, setActiveScenario] = useState<string | null>(null);
  const [result, setResult] = useState<SystemResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showJson, setShowJson] = useState(false);
  const [showTrace, setShowTrace] = useState(false);

  const runScenario = async (scenarioId: string) => {
    const scenario = DEMO_SCENARIOS.find((s) => s.id === scenarioId);
    if (!scenario) return;

    setActiveScenario(scenarioId);
    setResult(null);
    setError(null);
    setLoading(true);

    try {
      const response = await api.assessment(JSON.parse(JSON.stringify(scenario.state)), sessionId ?? undefined);
      if (!sessionId) onSessionCreated(response.session_id);
      setResult(response);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unexpected error');
    } finally {
      setLoading(false);
    }
  };

  const activeState = activeScenario ? DEMO_SCENARIOS.find((s) => s.id === activeScenario)?.state : null;

  return (
    <div className="flex flex-col h-full overflow-y-auto">
      {/* Demo Scenario Buttons */}
      <div className="p-4 border-b border-slate-700/50">
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Demo Scenarios</p>
        <div className="grid gap-2">
          {DEMO_SCENARIOS.map((s) => (
            <button
              key={s.id}
              id={`demo-${s.id}`}
              onClick={() => runScenario(s.id)}
              disabled={loading}
              className={`text-left rounded-lg border px-4 py-3 transition-all ${
                activeScenario === s.id
                  ? 'border-emerald-600 bg-emerald-900/30 text-emerald-100'
                  : 'border-slate-700 bg-slate-800/40 hover:border-slate-600 hover:bg-slate-800/80 text-slate-200'
              } disabled:opacity-50`}
            >
              <div className="flex items-center gap-3">
                <span className="text-lg">{s.icon}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold">{s.label}</span>
                    {activeScenario === s.id && loading ? (
                      <Spinner size={14} />
                    ) : (
                      <Play size={13} className="text-slate-500" />
                    )}
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5">{s.description}</p>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="m-4 bg-red-900/30 border border-red-700/40 rounded-lg p-3 text-xs text-red-300">
          Error: {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="p-4 space-y-4">
          {/* Detected Conditions */}
          {result.detected_conditions && result.detected_conditions.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Detected Conditions</p>
              <div className="flex flex-wrap gap-2">
                {result.detected_conditions.map((c) => (
                  <ConditionBadge key={c} condition={c} />
                ))}
              </div>
            </div>
          )}

          {/* Input state snapshot */}
          {activeState && (
            <div>
              <button
                onClick={() => setShowJson(!showJson)}
                className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-300 mb-2"
              >
                {showJson ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
                Environmental Profile Snapshot
              </button>
              {showJson && (
                <div className="bg-slate-900/60 border border-slate-700 rounded-lg p-3">
                  <dl className="grid grid-cols-2 gap-x-4 gap-y-1.5">
                    {Object.entries(activeState as Record<string, unknown>).map(([k, v]) => (
                      Array.isArray(v) ? (
                        <div key={k} className="col-span-2 flex justify-between gap-2">
                          <dt className="text-xs text-slate-500 capitalize">{k.replace(/_/g, ' ')}</dt>
                          <dd className="text-xs text-slate-300 text-right">{(v as string[]).join(', ')}</dd>
                        </div>
                      ) : (
                        <div key={k} className="flex justify-between gap-2">
                          <dt className="text-xs text-slate-500 capitalize">{k.replace(/_/g, ' ')}</dt>
                          <dd className="text-xs text-slate-300 text-right">{String(v)}</dd>
                        </div>
                      )
                    ))}
                  </dl>
                </div>
              )}
            </div>
          )}

          {/* Recommendations */}
          {result.recommendations && result.recommendations.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                <FlaskConical size={11} className="inline mr-1" />
                Evidence-Backed Recommendations ({result.recommendations.length})
              </p>
              <div className="space-y-2">
                {result.recommendations.map((rec, i) => (
                  <RecommendationCard key={i} rec={rec} index={i} />
                ))}
              </div>
            </div>
          )}

          {/* Reasoning Trace */}
          {result.reasoning_trace && (
            <div>
              <button
                onClick={() => setShowTrace(!showTrace)}
                className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-300 mb-2"
              >
                {showTrace ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
                Reasoning Trace (Transparency Audit)
              </button>
              {showTrace && <ReasoningTrace trace={result.reasoning_trace} />}
            </div>
          )}

          {/* Retrieved Evidence (from trace) */}
          {result.reasoning_trace?.retrieved_evidence && result.reasoning_trace.retrieved_evidence.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                Retrieved Scientific Evidence
              </p>
              <div className="space-y-2">
                {result.reasoning_trace.retrieved_evidence.map((ev) => (
                  <EvidenceCard key={ev.chunk_id} chunk={ev} />
                ))}
              </div>
            </div>
          )}

          {/* Limitations */}
          {result.limitations && result.limitations.length > 0 && (
            <div className="border border-amber-700/30 rounded-lg p-3 bg-amber-900/10">
              <p className="text-xs font-semibold text-amber-300 mb-1.5">Limitations</p>
              {result.limitations.map((l, i) => (
                <p key={i} className="text-xs text-amber-200/70">· {l}</p>
              ))}
            </div>
          )}
        </div>
      )}

      {!result && !loading && !error && (
        <div className="flex-1 flex items-center justify-center text-center p-8">
          <div>
            <FlaskConical size={32} className="text-slate-600 mx-auto mb-3" />
            <p className="text-sm text-slate-500">Select a demo scenario above to run a full structured assessment.</p>
          </div>
        </div>
      )}
    </div>
  );
}
