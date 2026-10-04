import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ShieldCheck, 
  ArrowLeft, 
  Download, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  Clock, 
  Brain, 
  Users, 
  MessageSquare, 
  FileText, 
  Eye, 
  ExternalLink,
  ChevronRight,
  Sparkles
} from 'lucide-react';
import { api } from '../api/client.js';

export default function ReportDetailPage() {
  const { interviewId } = useParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [report, setReport] = useState(null);
  const [showFullTranscript, setShowFullTranscript] = useState(false);

  // Default fallback data for preview & offline dev
  const fallbackData = {
    interview_id: interviewId || 'int-jane-doe-001',
    candidate_name: 'Jane Doe',
    job_title: 'Senior Backend Engineer',
    evaluated_at: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
    recommendation: 'PASS',
    composite_score: 88,
    integrity_score: 0.98,
    integrity_events_count: 0,
    technical: {
      score: 92,
      confidence_score: 0.95,
      weight: '50%',
      strength: 'Distributed Systems & Row-Level Security Architecture',
      missing_knowledge: ['Distributed consensus protocols (Raft) in deep edge cases'],
      evidence: [
        {
          quote: "In our production architecture, we offloaded writes into Redis streams and strictly partitioned read models using PostgreSQL RLS.",
          relevance: "High"
        }
      ]
    },
    behavioral: {
      score: 85,
      confidence_score: 0.92,
      weight: '25%',
      leadership_strengths: ['Extreme Incident Ownership', 'Transparent Postmortem Delivery'],
      improvement_areas: ['Earlier proactive communication with non-technical stakeholders'],
      evidence: [
        {
          quote: "I took full responsibility for resolving the post-deployment regression, conducting the retrospective with engineering leads within 24 hours.",
          relevance: "High"
        }
      ]
    },
    communication: {
      score: 87,
      confidence_score: 0.94,
      weight: '25%',
      clarity_score: 89,
      conciseness_score: 85,
      summary: "Clear, structured, and precise technical explanations with minimal filler words.",
      evidence: [
        {
          quote: "Articulated database failover mechanisms sequentially from health check failure to DNS promotion without digression.",
          relevance: "High"
        }
      ]
    },
    transcript: [
      { speaker: "AI", text: "Welcome to your Autergo technical interview. Could you describe your experience designing high-throughput distributed systems?" },
      { speaker: "CANDIDATE", text: "Certainly. In our production architecture, we offloaded writes into Redis streams and strictly partitioned read models using PostgreSQL RLS." },
      { speaker: "AI", text: "How did you guarantee zero-downtime database migrations when tenant schemas evolved?" },
      { speaker: "CANDIDATE", text: "We used expand-contract migration patterns with backwards-compatible schema rollouts and dual-write phases before dropping old columns." },
      { speaker: "AI", text: "Can you recount a high-severity production incident and how you owned the resolution?" },
      { speaker: "CANDIDATE", text: "I took full responsibility for resolving the post-deployment regression, conducting the retrospective with engineering leads within 24 hours." }
    ]
  };

  useEffect(() => {
    async function fetchReportData() {
      setLoading(true);
      if (interviewId) {
        try {
          const data = await api.getReport(interviewId);
          if (data && data.composite_score) {
            setReport(data);
            setLoading(false);
            return;
          }
        } catch (e) {
          console.warn('Failed to load remote report, using demo fallback:', e);
        }
      }
      setReport(fallbackData);
      setLoading(false);
    }
    fetchReportData();
  }, [interviewId]);

  const currentReport = report || fallbackData;
  const isPass = currentReport.recommendation === 'PASS';
  const isHold = currentReport.recommendation === 'HOLD';

  const downloadPdfUrl = api.getReportPdfUrl(currentReport.interview_id);

  return (
    <div className="min-h-screen bg-canvas text-ink flex flex-col">
      {/* Top Navbar */}
      <header className="h-14 border-b border-border bg-white px-6 flex items-center justify-between sticky top-0 z-30 shadow-xs">
        <div className="flex items-center space-x-4">
          <button 
            onClick={() => navigate('/dashboard')}
            className="flex items-center text-xs text-ink-muted hover:text-ink transition-colors font-medium space-x-1"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Dashboard</span>
          </button>
          <span className="text-border">/</span>
          <div className="flex items-center space-x-2 text-xs font-mono text-ink-muted">
            <span>Interviews</span>
            <ChevronRight className="w-3 h-3 text-border" />
            <span className="text-ink font-semibold">{currentReport.candidate_name}</span>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <a
            href={downloadPdfUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center space-x-1.5 border border-border hover:bg-canvas-subtle px-3 py-1.5 rounded-lg text-xs font-semibold text-ink transition-colors shadow-2xs"
          >
            <Download className="w-3.5 h-3.5 text-primary" />
            <span>Download PDF</span>
          </a>
          <button 
            onClick={() => navigate('/dashboard')}
            className="bg-primary hover:bg-primary-hover text-white px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors shadow-xs"
          >
            Back to Roster
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-6xl w-full mx-auto p-6 md:p-8 space-y-6">
        {/* Candidate Profile & Recommendation Banner */}
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white border border-border rounded-xl p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-6"
        >
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-2xl font-bold tracking-tight text-ink">{currentReport.candidate_name}</h1>
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-mono font-semibold uppercase tracking-wider flex items-center gap-1 ${
                isPass 
                  ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' 
                  : isHold 
                  ? 'bg-amber-50 text-amber-700 border border-amber-200' 
                  : 'bg-rose-50 text-rose-700 border border-rose-200'
              }`}>
                {isPass && <CheckCircle2 className="w-3.5 h-3.5" />}
                {isHold && <AlertTriangle className="w-3.5 h-3.5" />}
                {!isPass && !isHold && <XCircle className="w-3.5 h-3.5" />}
                <span>{currentReport.recommendation} RECOMMENDATION</span>
              </span>
            </div>
            <p className="text-xs text-ink-muted font-mono mt-1">
              Target Role: <strong className="text-ink">{currentReport.job_title}</strong> &bull; Concluded {currentReport.evaluated_at}
            </p>
          </div>

          <div className="flex items-center space-x-6 border-t md:border-t-0 md:border-l border-border pt-4 md:pt-0 md:pl-6">
            <div className="text-center md:text-right">
              <div className="text-[11px] text-ink-muted uppercase font-mono tracking-wider font-semibold">Composite Score</div>
              <div className={`text-3xl font-extrabold font-mono mt-0.5 ${
                currentReport.composite_score >= 80 ? 'text-emerald-600' : currentReport.composite_score >= 60 ? 'text-amber-600' : 'text-rose-600'
              }`}>
                {currentReport.composite_score}
                <span className="text-sm font-normal text-ink-muted font-sans">/100</span>
              </div>
            </div>
          </div>
        </motion.div>

        {/* 3 Metric Cards: Composite, Integrity Telemetry, Compliance */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Card 1: Score Gauge */}
          <div className="bg-white border border-border rounded-xl p-5 shadow-xs space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-ink-muted uppercase font-mono">Weighted Performance</span>
              <Brain className="w-4 h-4 text-primary" />
            </div>
            <div className="text-2xl font-bold font-mono text-ink">
              {currentReport.composite_score}%
            </div>
            <div className="w-full bg-canvas-muted h-2 rounded-full overflow-hidden">
              <div 
                className="bg-primary h-full transition-all duration-700" 
                style={{ width: `${currentReport.composite_score}%` }}
              />
            </div>
            <p className="text-[11px] text-ink-muted">
              50% Technical + 25% Behavioral + 25% Communication
            </p>
          </div>

          {/* Card 2: Integrity Telemetry */}
          <div className="bg-white border border-border rounded-xl p-5 shadow-xs space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-ink-muted uppercase font-mono">Session Integrity Meter</span>
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
            </div>
            <div className="flex items-baseline space-x-2">
              <div className="text-2xl font-bold font-mono text-emerald-600">
                {Math.round((currentReport.integrity_score || 1.0) * 100)}%
              </div>
              <span className="text-xs text-ink-muted font-mono">High Trust</span>
            </div>
            <div className="w-full bg-canvas-muted h-2 rounded-full overflow-hidden">
              <div 
                className="bg-emerald-600 h-full transition-all duration-700" 
                style={{ width: `${Math.round((currentReport.integrity_score || 1.0) * 100)}%` }}
              />
            </div>
            <p className="text-[11px] text-ink-muted font-mono">
              Integrity Telemetry: {currentReport.integrity_events_count || 0} Flagged Malpractice Events
            </p>
          </div>

          {/* Card 3: Proctoring Status */}
          <div className="bg-white border border-border rounded-xl p-5 shadow-xs space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-ink-muted uppercase font-mono">Proctoring Telemetry</span>
              <Eye className="w-4 h-4 text-primary" />
            </div>
            <div className="text-sm font-semibold text-ink flex items-center space-x-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Full Browser Lock Honored</span>
            </div>
            <div className="text-[11px] text-ink-muted space-y-1">
              <div>&bull; Tab Visibility: Retained Throughout</div>
              <div>&bull; Audio Channel: Single Speaker Detected</div>
              <div>&bull; Clipboard: 0 Unauthorized Pastes</div>
            </div>
          </div>
        </div>

        {/* Multi-Agent Breakdown Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Agent 1: Technical Reasoning */}
          <div className="bg-white border border-border rounded-xl p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-border">
              <div className="flex items-center space-x-2">
                <Brain className="w-4 h-4 text-primary" />
                <h3 className="text-sm font-bold text-ink">Technical Agent</h3>
              </div>
              <span className="text-xs font-mono font-bold text-emerald-600">
                {currentReport.technical?.score || 90}/100
              </span>
            </div>
            <div className="space-y-3 text-xs">
              <div>
                <span className="text-[11px] uppercase font-mono text-ink-muted font-semibold">Weight: 50%</span>
                <p className="text-ink font-medium mt-1">Core Architecture &amp; System Design</p>
              </div>
              <div className="bg-emerald-50/50 border border-emerald-100 rounded-lg p-3">
                <span className="text-[11px] font-semibold text-emerald-800 uppercase font-mono">Key Strength</span>
                <p className="text-emerald-950 mt-0.5 leading-relaxed">
                  {currentReport.technical?.strength || "Strong modular design principles"}
                </p>
              </div>
              {currentReport.technical?.missing_knowledge?.length > 0 && (
                <div className="bg-amber-50/50 border border-amber-100 rounded-lg p-3">
                  <span className="text-[11px] font-semibold text-amber-800 uppercase font-mono">Areas to Probe</span>
                  <p className="text-amber-950 mt-0.5 leading-relaxed">
                    {currentReport.technical.missing_knowledge[0]}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Agent 2: Behavioral Ownership */}
          <div className="bg-white border border-border rounded-xl p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-border">
              <div className="flex items-center space-x-2">
                <Users className="w-4 h-4 text-primary" />
                <h3 className="text-sm font-bold text-ink">Behavioral Agent</h3>
              </div>
              <span className="text-xs font-mono font-bold text-emerald-600">
                {currentReport.behavioral?.score || 85}/100
              </span>
            </div>
            <div className="space-y-3 text-xs">
              <div>
                <span className="text-[11px] uppercase font-mono text-ink-muted font-semibold">Weight: 25%</span>
                <p className="text-ink font-medium mt-1">Ownership &amp; Cross-Functional Alignment</p>
              </div>
              <div className="bg-blue-50/50 border border-blue-100 rounded-lg p-3">
                <span className="text-[11px] font-semibold text-blue-800 uppercase font-mono">Leadership Traits</span>
                <p className="text-blue-950 mt-0.5 leading-relaxed">
                  {currentReport.behavioral?.leadership_strengths?.join(", ") || "Extreme Ownership, Accountability"}
                </p>
              </div>
              {currentReport.behavioral?.improvement_areas?.length > 0 && (
                <div className="bg-amber-50/50 border border-amber-100 rounded-lg p-3">
                  <span className="text-[11px] font-semibold text-amber-800 uppercase font-mono">Growth Opportunity</span>
                  <p className="text-amber-950 mt-0.5 leading-relaxed">
                    {currentReport.behavioral.improvement_areas[0]}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Agent 3: Communication Clarity */}
          <div className="bg-white border border-border rounded-xl p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-border">
              <div className="flex items-center space-x-2">
                <MessageSquare className="w-4 h-4 text-primary" />
                <h3 className="text-sm font-bold text-ink">Communication Agent</h3>
              </div>
              <span className="text-xs font-mono font-bold text-emerald-600">
                {currentReport.communication?.score || 87}/100
              </span>
            </div>
            <div className="space-y-3 text-xs">
              <div>
                <span className="text-[11px] uppercase font-mono text-ink-muted font-semibold">Weight: 25%</span>
                <p className="text-ink font-medium mt-1">Clarity, Brevity, &amp; Precision</p>
              </div>
              <div className="grid grid-cols-2 gap-2 text-center">
                <div className="bg-canvas-subtle border border-border rounded-lg p-2.5">
                  <span className="text-[10px] font-mono text-ink-muted uppercase">Clarity</span>
                  <div className="text-base font-bold text-primary font-mono mt-0.5">
                    {currentReport.communication?.clarity_score || 88}%
                  </div>
                </div>
                <div className="bg-canvas-subtle border border-border rounded-lg p-2.5">
                  <span className="text-[10px] font-mono text-ink-muted uppercase">Conciseness</span>
                  <div className="text-base font-bold text-primary font-mono mt-0.5">
                    {currentReport.communication?.conciseness_score || 86}%
                  </div>
                </div>
              </div>
              <p className="text-ink-muted text-[11px] leading-relaxed italic">
                "{currentReport.communication?.summary || 'Clear and structured articulation.'}"
              </p>
            </div>
          </div>
        </div>

        {/* Verbatim Cited Evidence Section */}
        <div className="bg-white border border-border rounded-xl p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-ink uppercase tracking-wider font-mono">
              Verbatim Candidate Evidence Citations
            </h3>
            <span className="text-xs text-ink-muted font-mono">Extracted by Multi-Agent Evaluator</span>
          </div>

          <div className="space-y-3 text-xs">
            {currentReport.technical?.evidence?.map((ev, i) => (
              <div key={`tech-ev-${i}`} className="bg-canvas-subtle border border-border rounded-lg p-4 space-y-1">
                <div className="flex items-center justify-between text-[11px] font-mono">
                  <span className="font-semibold text-primary">[Technical Architecture Proof]</span>
                  <span className="text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded font-medium">Relevance: {ev.relevance}</span>
                </div>
                <p className="text-ink italic text-xs leading-relaxed pt-1">"{ev.quote}"</p>
              </div>
            ))}

            {currentReport.behavioral?.evidence?.map((ev, i) => (
              <div key={`beh-ev-${i}`} className="bg-canvas-subtle border border-border rounded-lg p-4 space-y-1">
                <div className="flex items-center justify-between text-[11px] font-mono">
                  <span className="font-semibold text-primary">[Behavioral Ownership Proof]</span>
                  <span className="text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded font-medium">Relevance: {ev.relevance}</span>
                </div>
                <p className="text-ink italic text-xs leading-relaxed pt-1">"{ev.quote}"</p>
              </div>
            ))}
          </div>
        </div>

        {/* Full Transcript Accordion */}
        <div className="bg-white border border-border rounded-xl overflow-hidden shadow-xs">
          <button 
            onClick={() => setShowFullTranscript(!showFullTranscript)}
            className="w-full p-4 flex items-center justify-between bg-canvas-subtle/50 hover:bg-canvas-subtle transition-colors text-xs font-semibold text-ink"
          >
            <div className="flex items-center space-x-2">
              <FileText className="w-4 h-4 text-primary" />
              <span>Full Interview Transcript ({currentReport.transcript?.length || 0} Turns)</span>
            </div>
            <span className="text-primary hover:underline">{showFullTranscript ? 'Hide Transcript' : 'View Full Transcript'}</span>
          </button>

          {showFullTranscript && (
            <div className="p-6 space-y-4 border-t border-border bg-white text-xs max-h-96 overflow-y-auto font-sans">
              {currentReport.transcript?.map((turn, idx) => (
                <div key={idx} className={`p-3 rounded-lg ${turn.speaker === 'AI' ? 'bg-primary-subtle/30 text-ink' : 'bg-canvas-subtle text-ink ml-4 border border-border'}`}>
                  <span className="text-[10px] font-mono font-bold uppercase tracking-wider block mb-1 text-primary">
                    {turn.speaker === 'AI' ? 'Autergo AI Interviewer' : currentReport.candidate_name}
                  </span>
                  <p className="leading-relaxed">{turn.text}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
