import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { 
  ShieldCheck, 
  Sparkles, 
  ArrowRight, 
  CheckCircle2, 
  Mic, 
  Cpu, 
  Lock, 
  Clock, 
  FileText,
  BarChart3,
  Layers,
  Radio,
  Zap,
  Terminal,
  Server,
  Activity,
  ChevronRight
} from 'lucide-react';

export default function LandingPage() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1, 
      transition: { staggerChildren: 0.12, delayChildren: 0.1 } 
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] } }
  };

  return (
    <div className="min-h-screen bg-[#07090e] text-[#f8fafc] flex flex-col justify-between selection:bg-indigo-500/30 selection:text-indigo-200 font-sans relative mesh-bg overflow-x-hidden">
      {/* Ambient background lighting */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-gradient-to-b from-indigo-600/15 via-purple-600/10 to-transparent blur-[140px] pointer-events-none -z-10" />
      <div className="absolute top-[800px] right-0 w-[500px] h-[400px] bg-cyan-600/10 blur-[150px] pointer-events-none -z-10" />

      {/* Top Navbar */}
      <nav className="sticky top-0 z-50 glass-panel border-b border-white/10 h-16 flex items-center px-8 justify-between max-w-7xl mx-auto w-full mt-2 rounded-2xl">
        <div className="flex items-center space-x-8">
          <Link to="/" className="flex items-center space-x-2.5 text-white font-semibold text-base tracking-tight group">
            <div className="w-8 h-8 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 group-hover:scale-105 transition-transform shadow-glow-primary">
              <ShieldCheck className="w-4 h-4 text-indigo-400" />
            </div>
            <span className="text-white font-semibold text-base tracking-tight">Autergo</span>
          </Link>
          <div className="hidden md:flex items-center space-x-6 text-xs font-medium text-slate-400">
            <a href="#how-it-works" className="hover:text-white transition-colors">How It Works</a>
            <a href="#features" className="hover:text-white transition-colors">Enterprise Features</a>
            <a href="#integrity" className="hover:text-white transition-colors">Integrity &amp; RLS</a>
            <Link to="/interview/demo-session" className="text-indigo-400 hover:text-indigo-300 font-semibold transition-colors flex items-center gap-1">
              <span>Interactive Voice Studio</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
        <div className="flex items-center space-x-3 text-xs font-medium">
          <Link to="/login" className="px-4 py-2 rounded-xl text-slate-300 hover:text-white hover:bg-white/5 transition-all">
            Sign In
          </Link>
          <Link to="/dashboard" className="bg-indigo-600 hover:bg-indigo-500 active:scale-95 text-white px-5 py-2 rounded-xl transition-all shadow-glow-primary font-medium flex items-center gap-1.5 cursor-pointer">
            <span>Open Portal</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="max-w-6xl mx-auto px-6 pt-20 pb-16 text-center z-10">
        <motion.div 
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="space-y-6"
        >
          {/* Badge */}
          <motion.div variants={itemVariants} className="inline-flex items-center space-x-2 bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 px-4 py-1.5 rounded-full text-xs font-medium shadow-glow-primary">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400 animate-pulse" />
            <span>Autonomous AI Technical Screening &bull; Sub-second Voice Loop</span>
          </motion.div>

          {/* Heading */}
          <motion.h1 
            variants={itemVariants} 
            className="text-4xl md:text-6xl lg:text-7xl font-bold tracking-tight text-white max-w-4xl mx-auto leading-tight"
          >
            Interview at Scale.<br />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-300 via-purple-300 to-cyan-300">
              Evaluate with Evidence.
            </span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p 
            variants={itemVariants} 
            className="text-base md:text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed font-normal"
          >
            Autergo is an autonomous, voice-first AI interviewer that conducts adaptive technical screening and delivers defensible, citation-backed scorecards.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div variants={itemVariants} className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-4 text-xs font-semibold">
            <Link 
              to="/dashboard" 
              className="w-full sm:w-auto bg-indigo-600 hover:bg-indigo-500 active:scale-95 text-white px-7 py-3.5 rounded-xl transition-all shadow-glow-primary flex items-center justify-center gap-2 cursor-pointer"
            >
              <span>Launch Recruiter Command Center</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link 
              to="/checkin" 
              className="w-full sm:w-auto glass-card hover:border-slate-500 active:scale-95 text-white px-7 py-3.5 rounded-xl transition-all flex items-center justify-center gap-2"
            >
              <span>Simulate Candidate Check-in</span>
              <ArrowRight className="w-4 h-4 text-slate-400" />
            </Link>
          </motion.div>

          {/* Interactive Voice Studio Terminal Preview */}
          <motion.div 
            variants={itemVariants}
            className="mt-14 glass-panel rounded-3xl border border-white/10 p-6 md:p-8 shadow-2xl text-left font-sans text-white max-w-4xl mx-auto overflow-hidden relative"
          >
            {/* Top Indicator bar */}
            <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-6">
              <div className="flex items-center space-x-2">
                <span className="w-3 h-3 rounded-full bg-rose-500/80"></span>
                <span className="w-3 h-3 rounded-full bg-amber-500/80"></span>
                <span className="w-3 h-3 rounded-full bg-emerald-500/80"></span>
                <span className="text-xs text-slate-400 font-mono pl-3">autergo://voice-studio/session-live</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 px-3 py-1 rounded-full flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
                  STAGE: DEEP_DIVE
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Transcript Preview */}
              <div className="md:col-span-2 space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono text-indigo-400 uppercase tracking-wider flex items-center gap-1.5 font-semibold">
                    <Radio className="w-3.5 h-3.5 animate-pulse" />
                    Candidate Verbatim Stream
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono">218ms TTFT</span>
                </div>
                <div className="glass-card p-4 rounded-2xl border-white/10 text-sm font-medium text-slate-200 leading-relaxed">
                  "In our payment engine, we enforced optimistic concurrency controls with Redis idempotency keys to stop race conditions while avoiding database-level row locks."
                </div>
                <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-3.5 text-xs text-slate-300 space-y-1 font-mono">
                  <div className="text-emerald-400 font-semibold flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <span>[NAT Evaluator Evidence Match]:</span>
                  </div>
                  <div>Extracted Competency: Distributed Concurrency &bull; Score: 94/100</div>
                </div>
              </div>

              {/* Real-time Telemetry Stats Card */}
              <div className="glass-card rounded-2xl p-5 flex flex-col justify-between border-white/10">
                <div>
                  <div className="text-[11px] font-mono text-slate-400 uppercase">Confidence Metric</div>
                  <div className="text-3xl font-bold text-white font-mono mt-1 flex items-baseline gap-1">
                    96.8<span className="text-sm font-normal text-indigo-400">%</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-1.5 mt-2 overflow-hidden">
                    <div className="bg-gradient-to-r from-indigo-500 to-cyan-400 h-full w-[96.8%]" />
                  </div>
                </div>

                <div className="pt-4 border-t border-white/10 space-y-2 font-mono">
                  <div className="flex justify-between text-[11px]">
                    <span className="text-slate-400">Audio Latency:</span>
                    <span className="text-emerald-400 font-semibold">&lt; 300 ms</span>
                  </div>
                  <div className="flex justify-between text-[11px]">
                    <span className="text-slate-400">Anti-Cheat Flags:</span>
                    <span className="text-emerald-400 font-semibold">0 Anomaly</span>
                  </div>
                  <div className="flex justify-between text-[11px]">
                    <span className="text-slate-400">Tenant RLS:</span>
                    <span className="text-indigo-400 font-semibold">ACTIVE</span>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </main>

      {/* Metrics Strip */}
      <section className="border-y border-white/10 py-16 px-6 glass-panel z-10">
        <div className="max-w-5xl mx-auto text-center">
          <span className="text-[11px] font-mono font-semibold uppercase text-indigo-400 tracking-wider">The Status Quo Broken</span>
          <h2 className="text-2xl md:text-3xl font-bold tracking-tight text-white mt-2">Manual Screening Does Not Scale</h2>
          <p className="text-xs md:text-sm text-slate-400 mt-2 max-w-xl mx-auto leading-relaxed">
            Senior engineers lose hundreds of hours each quarter conducting repetitive screening calls, resulting in interviewer fatigue, inconsistent scoring, and lost talent.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-10 text-left">
            <div className="glass-card rounded-2xl p-6 border-white/10">
              <div className="text-3xl font-bold font-mono text-white tracking-tight">45 min</div>
              <div className="text-xs font-semibold text-indigo-300 mt-2">Saved Per Phone Screen</div>
              <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">Engineers stop doing repetitive preliminary calls and focus on core products.</p>
            </div>
            <div className="glass-card rounded-2xl p-6 border-white/10">
              <div className="text-3xl font-bold font-mono text-white tracking-tight">3&times;</div>
              <div className="text-xs font-semibold text-purple-300 mt-2">Score Consistency</div>
              <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">Eliminates interviewer fatigue, unconscious bias, and arbitrary score variations.</p>
            </div>
            <div className="glass-card rounded-2xl p-6 border-white/10">
              <div className="text-3xl font-bold font-mono text-white tracking-tight">100%</div>
              <div className="text-xs font-semibold text-emerald-300 mt-2">Verifiable Citations</div>
              <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">Every score point links directly back to exact candidate quotes in the audio transcript.</p>
            </div>
          </div>
        </div>
      </section>

      {/* How it Works Flow */}
      <section id="how-it-works" className="py-24 px-6 max-w-6xl mx-auto z-10">
        <div className="text-center mb-16">
          <span className="text-[11px] font-mono font-semibold uppercase text-indigo-400 tracking-wider">The Autonomous Architecture</span>
          <h2 className="text-2xl md:text-3xl font-bold tracking-tight text-white mt-2">From Job Post to Evidence Report in One Flow</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="glass-card rounded-2xl p-6 border-white/10 space-y-4">
            <div className="w-10 h-10 rounded-xl bg-indigo-600/20 border border-indigo-500/30 text-indigo-400 font-mono font-bold flex items-center justify-center text-sm shadow-glow-primary">1</div>
            <h3 className="text-base font-semibold text-white">Parse Job Description with NER</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Upload your JD. Our extraction pipeline extracts core competencies, required depth, and edge cases into an adaptive interview blueprint.
            </p>
          </div>
          <div className="glass-card rounded-2xl p-6 border-white/10 space-y-4">
            <div className="w-10 h-10 rounded-xl bg-purple-600/20 border border-purple-500/30 text-purple-400 font-mono font-bold flex items-center justify-center text-sm">2</div>
            <h3 className="text-base font-semibold text-white">Candidates Speak Naturally</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Candidates join via zero-install guest links. Our 9-stage deterministic state machine conducts a live, sub-second voice interview.
            </p>
          </div>
          <div className="glass-card rounded-2xl p-6 border-white/10 space-y-4">
            <div className="w-10 h-10 rounded-xl bg-cyan-600/20 border border-cyan-500/30 text-cyan-400 font-mono font-bold flex items-center justify-center text-sm shadow-glow-cyan">3</div>
            <h3 className="text-base font-semibold text-white">Review Defensible Reports</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              NAT consensus agents analyze the full transcript, generating multi-dimensional radar scorecards with cited verbatim evidence.
            </p>
          </div>
        </div>
      </section>

      {/* Enterprise Security Section */}
      <section id="integrity" className="py-20 px-6 border-t border-white/10 glass-panel z-10">
        <div className="max-w-6xl mx-auto text-center space-y-4">
          <span className="text-[11px] font-mono uppercase text-indigo-400 tracking-wider">Enterprise Hardening</span>
          <h2 className="text-2xl md:text-3xl font-bold tracking-tight text-white">Built on Strict Tenant Isolation &amp; Guardrails</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-10 text-left">
            <div className="glass-card rounded-2xl p-6 border-white/10">
              <ShieldCheck className="w-7 h-7 text-indigo-400 mb-3" />
              <h4 className="text-sm font-semibold text-white">PostgreSQL Tenant RLS</h4>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">Row-Level Security guarantees candidate data and transcripts can never leak across tenant boundaries.</p>
            </div>
            <div className="glass-card rounded-2xl p-6 border-white/10">
              <Lock className="w-7 h-7 text-purple-400 mb-3" />
              <h4 className="text-sm font-semibold text-white">Llama Guard 3 Protection</h4>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">Real-time candidate speech filtering immediately neutralizes prompt injections and jailbreak attempts.</p>
            </div>
            <div className="glass-card rounded-2xl p-6 border-white/10">
              <Cpu className="w-7 h-7 text-cyan-400 mb-3" />
              <h4 className="text-sm font-semibold text-white">Deterministic FSM</h4>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">No hallucinated question flows. Every session strictly follows validated state machine transitions.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 py-8 px-8 text-xs text-slate-500 glass-panel z-10">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center space-x-2 text-white font-semibold">
            <ShieldCheck className="w-4 h-4 text-indigo-400" />
            <span>Autergo AI Interview System</span>
          </div>
          <div>&copy; 2026 Autergo Technologies Inc. Built with React &amp; Tailwind CSS.</div>
        </div>
      </footer>
    </div>
  );
}
