import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { 
  ShieldCheck, 
  Sparkles, 
  ArrowRight, 
  CheckCircle2, 
  Mic2, 
  Cpu, 
  Lock, 
  Clock, 
  FileText,
  BarChart3,
  Layers
} from 'lucide-react';

export default function LandingPage() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1, 
      transition: { staggerChildren: 0.1, delayChildren: 0.1 } 
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 16 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] } }
  };

  return (
    <div className="min-h-screen bg-canvas text-ink flex flex-col justify-between selection:bg-primary-subtle selection:text-primary">
      {/* Top Navbar */}
      <nav className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-border/80 h-16 flex items-center px-8 justify-between max-w-7xl mx-auto w-full">
        <div className="flex items-center space-x-8">
          <Link to="/" className="flex items-center space-x-2 text-ink font-semibold text-base tracking-tight">
            <ShieldCheck className="w-5 h-5 text-primary" />
            <span>Autergo</span>
          </Link>
          <div className="hidden md:flex items-center space-x-6 text-xs font-medium text-ink-muted">
            <a href="#how-it-works" className="hover:text-ink transition-colors">How It Works</a>
            <a href="#features" className="hover:text-ink transition-colors">Enterprise Features</a>
            <a href="#integrity" className="hover:text-ink transition-colors">Integrity & RLS</a>
            <Link to="/interview/demo-session" className="text-primary hover:text-primary-hover font-semibold transition-colors flex items-center gap-1">
              <span>Interactive Voice Demo</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
        <div className="flex items-center space-x-3 text-xs font-medium">
          <Link to="/login" className="px-3.5 py-1.5 rounded-full hover:bg-canvas-subtle transition-colors text-ink">
            Sign In
          </Link>
          <Link to="/dashboard" className="bg-primary hover:bg-primary-hover active:scale-95 text-white px-4 py-2 rounded-full transition-all shadow-xs">
            Open Portal
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="max-w-6xl mx-auto px-8 pt-20 pb-16 text-center">
        <motion.div 
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="space-y-6"
        >
          <motion.div variants={itemVariants} className="inline-flex items-center space-x-2 bg-primary-subtle text-primary border border-primary/20 px-3.5 py-1 rounded-full text-xs font-medium">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Baseline v2.0 Live &bull; Sub-second Adaptive Voice Screening</span>
          </motion.div>

          <motion.h1 
            variants={itemVariants} 
            className="text-4xl md:text-6xl font-semibold tracking-tight text-ink max-w-4xl mx-auto leading-tight md:leading-[1.1]"
          >
            Interview at Scale.<br />
            Evaluate with Evidence.
          </motion.h1>

          <motion.p 
            variants={itemVariants} 
            className="text-base md:text-lg text-ink-muted max-w-2xl mx-auto leading-relaxed"
          >
            Autergo is an autonomous, voice-first AI interviewer that conducts adaptive technical screening and delivers defensible, citation-backed scorecards.
          </motion.p>

          <motion.div variants={itemVariants} className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3 text-xs font-semibold">
            <Link 
              to="/dashboard" 
              className="w-full sm:w-auto bg-primary hover:bg-primary-hover active:scale-95 text-white px-6 py-3.5 rounded-full transition-all shadow-sm flex items-center justify-center gap-2"
            >
              <span>Launch Recruiter Command Center</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link 
              to="/checkin" 
              className="w-full sm:w-auto border border-border hover:bg-canvas-subtle active:scale-95 text-ink px-6 py-3.5 rounded-full transition-all"
            >
              Simulate Candidate Check-in &rarr;
            </Link>
          </motion.div>

          {/* Product Terminal Preview Card */}
          <motion.div 
            variants={itemVariants}
            className="mt-14 bg-dark-base rounded-2xl border border-dark-border p-6 shadow-2xl text-left font-sans text-white max-w-4xl mx-auto overflow-hidden"
          >
            <div className="flex items-center justify-between border-b border-dark-border pb-4 mb-6">
              <div className="flex items-center space-x-2">
                <span className="w-3 h-3 rounded-full bg-red-500/80"></span>
                <span className="w-3 h-3 rounded-full bg-amber-500/80"></span>
                <span className="w-3 h-3 rounded-full bg-emerald-500/80"></span>
                <span className="text-xs text-dark-muted font-mono pl-2">autergo://voice-session-active</span>
              </div>
              <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-0.5 rounded flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
                STATE: DEEP_DIVE
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="md:col-span-2 space-y-4">
                <div className="text-xs font-mono text-primary-ondark uppercase tracking-wider">Candidate Utterance &bull; Verbatim Voice Stream</div>
                <p className="text-sm font-medium text-dark-ink leading-relaxed">
                  "In our payment engine, we enforced optimistic concurrency controls with Redis idempotency keys to stop race conditions while avoiding database-level row locks."
                </p>
                <div className="bg-dark-surface border border-dark-border rounded-lg p-3 text-xs text-dark-muted space-y-1 font-mono">
                  <div className="text-emerald-400 font-semibold flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>[NAT Evaluator Evidence Match]:</span>
                  </div>
                  <div>Extracted Competency: Distributed Concurrency &bull; Score: 94/100</div>
                </div>
              </div>

              <div className="bg-dark-surface border border-dark-border rounded-xl p-4 flex flex-col justify-between">
                <div>
                  <div className="text-[11px] font-mono text-dark-muted uppercase">Confidence Metric</div>
                  <div className="text-2xl font-bold text-white font-mono mt-1">96.8%</div>
                </div>
                <div className="pt-4 border-t border-dark-border">
                  <div className="text-[11px] font-mono text-dark-muted">Voice Latency (TTFT)</div>
                  <div className="text-sm font-semibold text-emerald-400 font-mono">218 ms (Sub-second)</div>
                </div>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </main>

      {/* Problem Statement Strip */}
      <section className="bg-canvas-subtle border-y border-border py-20 px-8">
        <div className="max-w-4xl mx-auto text-center">
          <span className="text-[11px] font-mono font-semibold uppercase text-primary tracking-wider">The Status Quo</span>
          <h2 className="text-2xl md:text-3xl font-semibold tracking-tight text-ink mt-2">Manual screening does not scale</h2>
          <p className="text-xs md:text-sm text-ink-muted mt-3 max-w-xl mx-auto leading-relaxed">
            Engineers lose hundreds of hours each quarter conducting repetitive screening calls, resulting in interviewer fatigue, inconsistent scoring, and lost talent.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12 text-left">
            <div className="bg-white border border-border rounded-xl p-6 shadow-xs">
              <div className="text-3xl font-semibold font-mono text-ink tracking-tight">45 min</div>
              <div className="text-xs font-semibold text-ink mt-2">Lost per phone screen</div>
              <p className="text-[11px] text-ink-muted mt-1 leading-relaxed">Senior developers are pulled away from shipping core features.</p>
            </div>
            <div className="bg-white border border-border rounded-xl p-6 shadow-xs">
              <div className="text-3xl font-semibold font-mono text-ink tracking-tight">3&times;</div>
              <div className="text-xs font-semibold text-ink mt-2">Subjective score variance</div>
              <p className="text-[11px] text-ink-muted mt-1 leading-relaxed">Evaluation swings based on fatigue, mood, and unconscious bias.</p>
            </div>
            <div className="bg-white border border-border rounded-xl p-6 shadow-xs">
              <div className="text-3xl font-semibold font-mono text-ink tracking-tight">100%</div>
              <div className="text-xs font-semibold text-ink mt-2">Verifiable citations</div>
              <p className="text-[11px] text-ink-muted mt-1 leading-relaxed">Every score point links directly back to candidate quotes.</p>
            </div>
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section id="how-it-works" className="py-24 px-8 max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <span className="text-[11px] font-mono font-semibold uppercase text-primary tracking-wider">The Flow</span>
          <h2 className="text-2xl md:text-3xl font-semibold tracking-tight text-ink mt-2">From Job Post to Evidence Report in One Flow</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="space-y-3">
            <div className="w-8 h-8 rounded-full bg-primary-subtle text-primary font-mono font-semibold flex items-center justify-center text-xs">1</div>
            <h3 class="text-sm font-semibold text-ink">Parse JD with GLiNER</h3>
            <p className="text-xs text-ink-muted leading-relaxed">
              Paste your JD. Our extraction pipeline extracts skills, competencies, and depth weights into an adaptive interview blueprint.
            </p>
          </div>
          <div className="space-y-3">
            <div className="w-8 h-8 rounded-full bg-primary-subtle text-primary font-mono font-semibold flex items-center justify-center text-xs">2</div>
            <h3 class="text-sm font-semibold text-ink">Candidates Speak Naturally</h3>
            <p className="text-xs text-ink-muted leading-relaxed">
              Candidates join via zero-install guest links. Our 10-stage deterministic state machine conducts a live, voice-to-voice interview.
            </p>
          </div>
          <div className="space-y-3">
            <div className="w-8 h-8 rounded-full bg-primary-subtle text-primary font-mono font-semibold flex items-center justify-center text-xs">3</div>
            <h3 class="text-sm font-semibold text-ink">Review Defensible Reports</h3>
            <p className="text-xs text-ink-muted leading-relaxed">
              Celery worker NAT agents analyze full transcripts, generating multi-dimensional radar scorecards with cited verbatim evidence.
            </p>
          </div>
        </div>
      </section>

      {/* Integrity & Enterprise Security */}
      <section id="integrity" className="bg-dark-base text-white py-20 px-8 border-t border-dark-border">
        <div className="max-w-6xl mx-auto text-center space-y-4">
          <span className="text-[11px] font-mono uppercase text-primary-ondark tracking-wider">Adversarial Resistance</span>
          <h2 className="text-2xl md:text-3xl font-semibold tracking-tight">Built on Strict Isolation & Guardrails</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-10 text-left">
            <div className="bg-dark-surface border border-dark-border rounded-xl p-6">
              <ShieldCheck className="w-6 h-6 text-primary-ondark mb-3" />
              <h4 className="text-sm font-semibold text-white">PostgreSQL Tenant RLS</h4>
              <p className="text-xs text-dark-muted mt-1 leading-relaxed">Row-Level Security guarantees candidate data and transcripts can never leak across tenant boundaries.</p>
            </div>
            <div className="bg-dark-surface border border-dark-border rounded-xl p-6">
              <Lock className="w-6 h-6 text-primary-ondark mb-3" />
              <h4 className="text-sm font-semibold text-white">Llama Guard 3 Protection</h4>
              <p className="text-xs text-dark-muted mt-1 leading-relaxed">Real-time candidate speech filtering immediately neutralizes prompt injections and jailbreak attempts.</p>
            </div>
            <div className="bg-dark-surface border border-dark-border rounded-xl p-6">
              <Cpu className="w-6 h-6 text-primary-ondark mb-3" />
              <h4 className="text-sm font-semibold text-white">Deterministic State Machine</h4>
              <p className="text-xs text-dark-muted mt-1 leading-relaxed">No hallucinated question flows. Every session strictly follows validated state machine transitions.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-canvas-subtle border-t border-border py-8 px-8 text-xs text-ink-muted">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center space-x-2 text-ink font-semibold">
            <ShieldCheck className="w-4 h-4 text-primary" />
            <span>Autergo AI Interview System</span>
          </div>
          <div>&copy; 2026 Autergo Technologies Inc. Built with React &amp; Tailwind CSS.</div>
        </div>
      </footer>
    </div>
  );
}
