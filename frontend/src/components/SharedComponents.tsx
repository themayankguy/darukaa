import type { RetrievedEvidenceChunk, ReasoningTraceResponse, RecommendationResponseItem } from '../services/api';
import { BookOpen, FlaskConical, Clock, TrendingUp, AlertTriangle, CheckCircle, ChevronDown, ChevronRight } from 'lucide-react';
import { useState } from 'react';

// ─── Evidence Card ────────────────────────────────────────────────────────────

interface EvidenceCardProps {
  chunk: RetrievedEvidenceChunk;
}

export function EvidenceCard({ chunk }: EvidenceCardProps) {
  const [expanded, setExpanded] = useState(false);
  const score = Math.round(chunk.relevance_score * 100);

  return (
    <div className="border border-slate-700 rounded-lg bg-slate-900/60 overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full text-left px-4 py-3 flex items-start gap-3 hover:bg-slate-800/40 transition-colors"
      >
        <BookOpen size={14} className="text-emerald-400 mt-0.5 shrink-0" />
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <span className="text-xs font-medium text-slate-300 truncate">{chunk.source_document}</span>
            <span className={`text-xs font-semibold px-1.5 py-0.5 rounded shrink-0 ${score >= 70 ? 'bg-emerald-900/60 text-emerald-300' : score >= 50 ? 'bg-amber-900/60 text-amber-300' : 'bg-slate-700 text-slate-400'}`}>
              {score}%
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5 line-clamp-2">{chunk.excerpt}</p>
        </div>
        <span className="text-slate-500 shrink-0">{expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}</span>
      </button>
      {expanded && (
        <div className="px-4 pb-3 border-t border-slate-700/50">
          <p className="text-xs text-slate-300 mt-3 leading-relaxed">{chunk.excerpt}</p>
          {chunk.key_claims.length > 0 && (
            <div className="mt-3">
              <p className="text-xs font-semibold text-slate-400 mb-1.5">Key claims</p>
              <ul className="space-y-1">
                {chunk.key_claims.map((claim, i) => (
                  <li key={i} className="flex items-start gap-2 text-xs text-slate-300">
                    <CheckCircle size={12} className="text-emerald-400 mt-0.5 shrink-0" />
                    {claim}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Recommendation Card ──────────────────────────────────────────────────────

interface RecommendationCardProps {
  rec: RecommendationResponseItem;
  index: number;
}

export function RecommendationCard({ rec, index }: RecommendationCardProps) {
  const [expanded, setExpanded] = useState(false);

  const confidenceColor =
    rec.confidence === 'high' ? 'text-emerald-300 bg-emerald-900/40 border-emerald-700/50' :
    rec.confidence === 'medium' ? 'text-amber-300 bg-amber-900/40 border-amber-700/50' :
    'text-slate-300 bg-slate-800 border-slate-600';

  return (
    <div className="border border-slate-700 rounded-xl bg-slate-900/50 overflow-hidden">
      <div className="p-4">
        <div className="flex items-start gap-3">
          <div className="w-6 h-6 rounded-full bg-emerald-900/60 border border-emerald-700/50 flex items-center justify-center shrink-0 mt-0.5">
            <span className="text-xs font-bold text-emerald-300">{index + 1}</span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-slate-100 leading-snug">{rec.action}</p>
            <div className="flex flex-wrap gap-2 mt-2">
              <span className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded border font-medium ${confidenceColor}`}>
                <FlaskConical size={10} />
                {rec.confidence} confidence
              </span>
              <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded border border-slate-600 text-slate-400 bg-slate-800">
                <Clock size={10} />
                {rec.time_horizon}
              </span>
            </div>
            <div className="flex flex-wrap gap-1 mt-2">
              {rec.impacted_metrics.map((m) => (
                <span key={m} className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                  {m}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-3 pl-9">
          <p className="text-xs text-slate-300 leading-relaxed">{rec.why_it_works}</p>
          {rec.quantitative_estimate && (
            <div className="mt-2 flex items-center gap-1.5 text-xs text-emerald-300">
              <TrendingUp size={12} />
              <span>{rec.quantitative_estimate}</span>
            </div>
          )}
        </div>
      </div>

      {(rec.evidence.length > 0 || rec.limitations.length > 0) && (
        <div className="border-t border-slate-700/50">
          <button
            onClick={() => setExpanded(!expanded)}
            className="w-full px-4 py-2 text-xs text-slate-400 hover:text-slate-300 flex items-center gap-1.5 hover:bg-slate-800/30 transition-colors"
          >
            {expanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
            {rec.evidence.length} evidence source{rec.evidence.length !== 1 ? 's' : ''}
            {rec.limitations.length > 0 && ` · ${rec.limitations.length} limitation${rec.limitations.length !== 1 ? 's' : ''}`}
          </button>
          {expanded && (
            <div className="px-4 pb-4 space-y-3">
              {rec.evidence.length > 0 && (
                <div className="space-y-2">
                  {rec.evidence.map((ev) => (
                    <EvidenceCard key={ev.chunk_id} chunk={ev} />
                  ))}
                </div>
              )}
              {rec.limitations.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-slate-400 mb-1.5">Limitations</p>
                  {rec.limitations.map((lim, i) => (
                    <div key={i} className="flex items-start gap-2 text-xs text-amber-300/80">
                      <AlertTriangle size={11} className="mt-0.5 shrink-0" />
                      {lim}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Reasoning Trace ──────────────────────────────────────────────────────────

interface ReasoningTraceProps {
  trace: ReasoningTraceResponse;
}

interface TraceSection {
  label: string;
  items: string[];
  color: string;
}

export function ReasoningTrace({ trace }: ReasoningTraceProps) {
  const sections: TraceSection[] = [
    { label: 'Input Factors', items: trace.input_factors, color: 'text-blue-300' },
    { label: 'Detected Conditions', items: trace.detected_conditions, color: 'text-amber-300' },
    { label: 'Cross-Variable Relationships', items: trace.cross_variable_relationships, color: 'text-purple-300' },
    { label: 'Candidate Interventions', items: trace.candidate_interventions, color: 'text-cyan-300' },
    { label: 'Validated Claims', items: trace.validated_claims, color: 'text-emerald-300' },
  ];

  return (
    <div className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-2">
        {sections.map((s) => (
          s.items.length > 0 && (
            <div key={s.label} className="bg-slate-900/60 border border-slate-700 rounded-lg p-3">
              <p className={`text-xs font-semibold mb-2 ${s.color}`}>{s.label}</p>
              <ul className="space-y-1">
                {s.items.map((item, i) => (
                  <li key={i} className="text-xs text-slate-300 leading-snug flex items-start gap-1.5">
                    <span className="text-slate-600 shrink-0">·</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          )
        ))}
      </div>
      {trace.decision_rationale && (
        <div className="bg-slate-800/60 border border-slate-600 rounded-lg p-4">
          <p className="text-xs font-semibold text-slate-300 mb-1.5">Decision Rationale</p>
          <p className="text-xs text-slate-300 leading-relaxed">{trace.decision_rationale}</p>
        </div>
      )}
    </div>
  );
}

// ─── Condition Badge ──────────────────────────────────────────────────────────

interface ConditionBadgeProps {
  condition: string;
}

const CONDITION_STYLES: Record<string, string> = {
  critical: 'bg-red-900/50 text-red-300 border-red-700/50',
  severe: 'bg-red-900/40 text-red-300 border-red-700/40',
  low: 'bg-amber-900/40 text-amber-300 border-amber-700/40',
  degraded: 'bg-orange-900/40 text-orange-300 border-orange-700/40',
  poor: 'bg-orange-900/40 text-orange-300 border-orange-700/40',
};

export function ConditionBadge({ condition }: ConditionBadgeProps) {
  const lower = condition.toLowerCase();
  const style = Object.keys(CONDITION_STYLES).find((k) => lower.includes(k));
  const cls = style ? CONDITION_STYLES[style] : 'bg-slate-800 text-slate-300 border-slate-600';

  return (
    <span className={`inline-block text-xs px-2.5 py-1 rounded-full border font-medium ${cls}`}>
      {condition}
    </span>
  );
}

// ─── Loading Spinner ──────────────────────────────────────────────────────────

export function Spinner({ size = 16 }: { size?: number }) {
  return (
    <svg
      style={{ width: size, height: size }}
      className="animate-spin text-emerald-400"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  );
}

// ─── Status Pill ──────────────────────────────────────────────────────────────

export function StatusPill({ status }: { status: 'online' | 'offline' | 'checking' }) {
  const styles = {
    online: 'bg-emerald-400',
    offline: 'bg-red-400',
    checking: 'bg-amber-400 animate-pulse',
  };
  const labels = { online: 'API Online', offline: 'API Offline', checking: 'Connecting…' };

  return (
    <div className="flex items-center gap-1.5">
      <div className={`w-1.5 h-1.5 rounded-full ${styles[status]}`} />
      <span className="text-xs text-slate-400">{labels[status]}</span>
    </div>
  );
}
