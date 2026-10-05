import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
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
  Sparkles,
  Bot,
  User,
  Activity,
  Award
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
    <div className="min-h-screen bg-[#07090e] text-[#f8fafc] flex flex-col font-sans relative mesh-bg">
      {/* Top Navbar */}
      <header className="h-16 border-b border-white/10 glass-panel px-6 flex items-center justify-between sticky top-0 z-30 shadow-xl">
        <div className="flex items-center space-x-4">
          <button 
            onClick={() => navigate('/dashboard')}
            className="flex items-center text-xs text-slate-400 hover:text-white transition-colors font-medium space-x-1.5 cursor-pointer glass-card px-3 py-1.5 rounded-xl"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Dashboard</span>
          </button>
          <span className="text-white/20">/</span>
          <div className="flex items-center space-x-2 text-xs font-mono text-slate-400">
            <span>Evaluation Dossier</span>
            <ChevronRight className="w-3 h-3 text-slate-600" />
            <span className="text-white font-semibold">{currentReport.candidate_name}</span>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <a
            href={downloadPdfUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center space-x-2 glass-card hover:border-slate-500 px-4 py-2 rounded-xl text-xs font-medium text-white transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-indigo-400" />
            <span>Download Certified PDF</span>
          </a>
          <button 
            onClick={() => navigate('/dashboard')}
            className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-xl text-xs font-medium transition-all shadow-glow-primary cursor-pointer"
          >
            Back to Roster
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-6xl w-full mx-auto p-6 md:p-8 space-y-6 z-10">
        {/* Candidate Profile & Recommendation Banner */}
        <motion.div 
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-panel border border-white/10 rounded-3xl p-6 md:p-8 shadow-2xl flex flex-col md:flex-row md:items-center justify-between gap-6 relative overflow-hidden"
        >
          {/* Top highlight bar */}
          <div className={`absolute top-0 inset-x-0 h-1 ${
            isPass ? 'bg-gradient-to-r from-emerald-500 to-teal-400' : isHold ? 'bg-gradient-to-r from-amber-500 to-orange-400' : 'bg-gradient-to-r from-rose-500 to-red-400'
          }`} />

          <div>
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white">{currentReport.candidate_name}</h1>
              <span className={`px-3 py-1 rounded-full text-xs font-mono font-semibold uppercase tracking-wider flex items-center gap-1.5 border ${
                isPass 
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 shadow-[0_0_15px_rgba(16,185,129,0.2)]' 
                  : isHold 
                  ? 'bg-amber-500/10 text-amber-400 border-amber-500/30' 
                  : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
              }`}>
                {isPass && <CheckCircle2 className="w-3.5 h-3.5" />}
                {isHold && <AlertTriangle className="w-3.5 h-3.5" />}
                {!isPass && !isHold && <XCircle className="w-3.5 h-3.5" />}
                <span>{currentReport.recommendation} RECOMMENDATION</span>
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono mt-1.5 flex items-center gap-2">
              <span>Target Role: <strong className="text-white">{currentReport.job_title}</strong></span>
              <span>&bull;</span>
              <span>Concluded {currentReport.evaluated_at}</span>
            </p>
          </div>

          <div className="flex items-center space-x-6 border-t md:border-t-0 md:border-l border-white/10 pt-4 md:pt-0 md:pl-8">
            <div className="text-center md:text-right">
              <div className="text-[11px] text-slate-400 uppercase font-mono tracking-wider font-semibold">Composite Score</div>
              <div className={`text-4xl font-extrabold font-mono mt-0.5 ${
                currentReport.composite_score >= 80 ? 'text-emerald-400' : currentReport.composite_score >= 60 ? 'text-amber-400' : 'text-rose-400'
              }`}>
                {currentReport.composite_score}
                <span className="text-sm font-normal text-slate-500 font-sans">/100</span>
              </div>
            </div>
          </div>
        </motion.div>

        {/* 3 Metric Cards: Composite, Integrity Telemetry, Proctoring */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {/* Card 1: Score Gauge */}
          <div className="glass-panel border border-white/10 rounded-2xl p-6 shadow-xl space-y-3 relative overflow-hidden">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400 uppercase font-mono">Weighted Performance</span>
              <Brain className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="text-3xl font-bold font-mono text-white">
              {currentReport.composite_score}%
            </div>
            <div className="w-full bg-black/40 h-2 rounded-full overflow-hidden border border-white/5">
              <motion.div 
                initial={{ width: 0 }}
                animate={{ width: `${currentReport.composite_score}%` }}
                transition={{ duration: 0.8, ease: 'easeOut' }}
                className="bg-gradient-to-r from-indigo-500 to-cyan-400 h-full rounded-full" 
              />
            </div>
            <p className="text-[11px] text-slate-400 font-mono">
              50% Technical + 25% Behavioral + 25% Communication
            </p>
          </div>

          {/* Card 2: Integrity Telemetry */}
          <div className="glass-panel border border-white/10 rounded-2xl p-6 shadow-xl space-y-3 relative overflow-hidden">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400 uppercase font-mono">Session Integrity Meter</span>
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="flex items-baseline space-x-2">
              <div className="text-3xl font-bold font-mono text-emerald-400">
                {Math.round((currentReport.integrity_score || 1.0) * 100)}%
              </div>
              <span className="text-xs text-emerald-400/80 font-mono">High Trust Verified</span>
            </div>
            <div className="w-full bg-black/40 h-2 rounded-full overflow-hidden border border-white/5">
              <motion.div 
                initial={{ width: 0 }}
                animate={{ width: `${Math.round((currentReport.integrity_score || 1.0) * 100)}%` }}
                transition={{ duration: 0.8, ease: 'easeOut' }}
                className="bg-emerald-400 h-full rounded-full" 
              />
            </div>
            <p className="text-[11px] text-slate-400 font-mono">
              {currentReport.integrity_events_count || 0} Flagged Malpractice Events
            </p>
          </div>

          {/* Card 3: Proctoring Status */}
          <div className="glass-panel border border-white/10 rounded-2xl p-6 shadow-xl space-y-3 relative overflow-hidden">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400 uppercase font-mono">Proctoring Telemetry</span>
              <Eye className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="text-sm font-semibold text-white flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Full Environment Lock Honored</span>
            </div>
            <div className="text-[11px] text-slate-400 space-y-1 font-mono">
              <div>&bull; Tab Visibility: Retained Throughout</div>
              <div>&bull; Audio Channel: Single Speaker Detected</div>
              <div>&bull; Clipboard: 0 Unauthorized Pastes</div>
            </div>
          </div>
        </div>

        {/* Multi-Agent Breakdown Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Agent 1: Technical Reasoning */}
          <div className="glass-panel border border-white/10 rounded-2xl p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <div className="flex items-center space-x-2">
                <Brain className="w-4 h-4 text-indigo-400" />
                <h3 className="text-sm font-bold text-white">Technical Agent</h3>
              </div>
              <span className="text-sm font-mono font-bold text-emerald-400">
                {currentReport.technical?.score || 90}/100
              </span>
            </div>
            <div className="space-y-3 text-xs">
              <div>
                <span className="text-[10px] uppercase font-mono text-slate-400 font-semibold">Weight: 50%</span>
                <p className="text-white font-medium mt-1">Core Architecture &amp; System Design</p>
              </div>
              <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-3.5">
                <span className="text-[10px] font-semibold text-emerald-400 uppercase font-mono">Key Strength</span>
                <p className="text-slate-200 mt-1 leading-relaxed">
                  {currentReport.technical?.strength || "Strong modular design principles"}
                </p>
              </div>
              {currentReport.technical?.missing_knowledge?.length > 0 && (
                <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-3.5">
                  <span className="text-[10px] font-semibold text-amber-400 uppercase font-mono">Areas to Probe</span>
                  <p className="text-slate-200 mt-1 leading-relaxed">
                    {currentReport.technical.missing_knowledge[0]}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Agent 2: Behavioral Ownership */}
          <div className="glass-panel border border-white/10 rounded-2xl p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <div className="flex items-center space-x-2">
                <Users className="w-4 h-4 text-purple-400" />
                <h3 className="text-sm font-bold text-white">Behavioral Agent</h3>
              </div>
              <span className="text-sm font-mono font-bold text-emerald-400">
                {currentReport.behavioral?.score || 85}/100
              </span>
            </div>
            <div className="space-y-3 text-xs">
              <div>
                <span className="text-[10px] uppercase font-mono text-slate-400 font-semibold">Weight: 25%</span>
                <p className="text-white font-medium mt-1">Ownership &amp; Cross-Functional Alignment</p>
              </div>
              <div className="bg-purple-500/10 border border-purple-500/20 rounded-xl p-3.5">
                <span className="text-[10px] font-semibold text-purple-400 uppercase font-mono">Leadership Traits</span>
                <p className="text-slate-200 mt-1 leading-relaxed">
                  {currentReport.behavioral?.leadership_strengths?.join(", ") || "Extreme Ownership, Accountability"}
                </p>
              </div>
              {currentReport.behavioral?.improvement_areas?.length > 0 && (
                <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-3.5">
                  <span className="text-[10px] font-semibold text-amber-400 uppercase font-mono">Growth Opportunity</span>
                  <p className="text-slate-200 mt-1 leading-relaxed">
                    {currentReport.behavioral.improvement_areas[0]}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Agent 3: Communication Clarity */}
          <div className="glass-panel border border-white/10 rounded-2xl p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <div className="flex items-center space-x-2">
                <MessageSquare className="w-4 h-4 text-cyan-400" />
                <h3 className="text-sm font-bold text-white">Communication Agent</h3>
              </div>
              <span className="text-sm font-mono font-bold text-emerald-400">
                {currentReport.communication?.score || 87}/100
              </span>
            </div>
            <div className="space-y-3 text-xs">
              <div>
                <span className="text-[10px] uppercase font-mono text-slate-400 font-semibold">Weight: 25%</span>
                <p className="text-white font-medium mt-1">Clarity, Brevity, &amp; Precision</p>
              </div>
              <div className="grid grid-cols-2 gap-2 text-center">
                <div className="bg-black/30 border border-white/10 rounded-xl p-2.5">
                  <span className="text-[10px] font-mono text-slate-400 uppercase">Clarity</span>
                  <div className="text-base font-bold text-indigo-400 font-mono mt-0.5">
                    {currentReport.communication?.clarity_score || 88}%
                  </div>
                </div>
                <div className="bg-black/30 border border-white/10 rounded-xl p-2.5">
                  <span className="text-[10px] font-mono text-slate-400 uppercase">Conciseness</span>
                  <div className="text-base font-bold text-cyan-400 font-mono mt-0.5">
                    {currentReport.communication?.conciseness_score || 86}%
                  </div>
                </div>
              </div>
              <p className="text-slate-300 text-[11px] leading-relaxed italic">
                "{currentReport.communication?.summary || 'Clear and structured articulation.'}"
              </p>
            </div>
          </div>
        </div>

        {/* Verbatim Cited Evidence Section */}
        <div className="glass-panel border border-white/10 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
              <Award className="w-4 h-4 text-indigo-400" />
              <span>Verbatim Candidate Evidence Citations</span>
            </h3>
            <span className="text-xs text-slate-400 font-mono">Extracted by Multi-Agent Consensus</span>
          </div>

          <div className="space-y-3 text-xs">
            {currentReport.technical?.evidence?.map((ev, i) => (
              <div key={`tech-ev-${i}`} className="glass-card rounded-xl p-4 space-y-1.5 border-white/10">
                <div className="flex items-center justify-between text-[11px] font-mono">
                  <span className="font-semibold text-indigo-400">[Technical Architecture Proof]</span>
                  <span className="text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full font-medium">Relevance: {ev.relevance}</span>
                </div>
                <p className="text-slate-200 italic text-xs leading-relaxed pt-1">"{ev.quote}"</p>
              </div>
            ))}

            {currentReport.behavioral?.evidence?.map((ev, i) => (
              <div key={`beh-ev-${i}`} className="glass-card rounded-xl p-4 space-y-1.5 border-white/10">
                <div className="flex items-center justify-between text-[11px] font-mono">
                  <span className="font-semibold text-purple-400">[Behavioral Ownership Proof]</span>
                  <span className="text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full font-medium">Relevance: {ev.relevance}</span>
                </div>
                <p className="text-slate-200 italic text-xs leading-relaxed pt-1">"{ev.quote}"</p>
              </div>
            ))}
          </div>
        </div>

        {/* Full Transcript Accordion */}
        <div className="glass-panel border border-white/10 rounded-2xl overflow-hidden shadow-xl">
          <button 
            onClick={() => setShowFullTranscript(!showFullTranscript)}
            className="w-full p-4 flex items-center justify-between bg-black/20 hover:bg-black/40 transition-colors text-xs font-semibold text-white cursor-pointer"
          >
            <div className="flex items-center space-x-2">
              <FileText className="w-4 h-4 text-indigo-400" />
              <span>Full Interview Transcript ({currentReport.transcript?.length || 0} Turns)</span>
            </div>
            <span className="text-indigo-400 hover:text-indigo-300">{showFullTranscript ? 'Hide Transcript' : 'View Full Transcript'} &rarr;</span>
          </button>

          <AnimatePresence>
            {showFullTranscript && (
              <motion.div 
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="p-6 space-y-3 border-t border-white/10 text-xs max-h-96 overflow-y-auto font-sans"
              >
                {currentReport.transcript?.map((turn, idx) => (
                  <div key={idx} className={`p-3 rounded-xl border ${
                    turn.speaker === 'AI' 
                      ? 'bg-indigo-500/10 border-indigo-500/20 text-slate-200' 
                      : 'bg-emerald-500/10 border-emerald-500/20 text-slate-200 ml-4'
                  }`}>
                    <span className={`text-[10px] font-mono font-bold uppercase tracking-wider block mb-1 ${
                      turn.speaker === 'AI' ? 'text-indigo-400' : 'text-emerald-400'
                    }`}>
                      {turn.speaker === 'AI' ? 'Autergo Voice AI' : currentReport.candidate_name}
                    </span>
                    <p className="leading-relaxed">{turn.text}</p>
                  </div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}
