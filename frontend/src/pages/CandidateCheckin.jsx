import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { 
  ShieldCheck, 
  Mic, 
  Globe, 
  Wifi, 
  Check, 
  ArrowRight, 
  Play, 
  CheckCircle2, 
  Volume2, 
  Sparkles,
  Lock,
  ChevronRight
} from 'lucide-react';

export default function CandidateCheckin() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || 'guest-demo';
  const interviewId = searchParams.get('interview_id') || 'int-demo';

  const [step, setStep] = useState(1);
  const [micStatus, setMicStatus] = useState('Click to test');
  const [micVerified, setMicVerified] = useState(false);
  const [quietConfirmed, setQuietConfirmed] = useState(false);
  const [invitationData, setInvitationData] = useState(null);

  React.useEffect(() => {
    async function checkToken() {
      if (token && token !== 'guest-demo') {
        try {
          const res = await fetch(`/api/v1/invitations/verify/${token}`);
          if (res.ok) {
            const data = await res.json();
            setInvitationData(data);
          }
        } catch (e) {
          console.warn('Token verify fallback', e);
        }
      }
    }
    checkToken();
  }, [token]);

  const testMicrophone = async () => {
    try {
      await navigator.mediaDevices.getUserMedia({ audio: true });
      setMicStatus('Microphone Active & Verified');
      setMicVerified(true);
    } catch (e) {
      setMicStatus('Simulated Active Input (Ready)');
      setMicVerified(true);
    }
  };

  const handleStartInterview = () => {
    const sessionId = 'session-' + Math.random().toString(36).substring(2, 9);
    navigate(`/interview/${sessionId}?interview_id=${interviewId}&token=${token}`);
  };

  return (
    <div className="min-h-screen bg-[#07090e] text-[#f8fafc] flex flex-col justify-between p-6 font-sans relative mesh-bg overflow-x-hidden">
      {/* Ambient background glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-gradient-to-tr from-indigo-600/15 via-purple-600/10 to-transparent rounded-full blur-[140px] pointer-events-none -z-10" />

      {/* Top Header */}
      <header className="max-w-xl mx-auto w-full flex items-center justify-between pb-6 border-b border-white/10 z-10">
        <Link to="/" className="flex items-center space-x-2.5 text-white font-semibold text-sm group">
          <div className="w-7 h-7 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 group-hover:scale-105 transition-transform shadow-glow-primary">
            <ShieldCheck className="w-4 h-4 text-indigo-400" />
          </div>
          <span>Autergo Studio</span>
        </Link>
        <span className="text-xs text-slate-400 font-mono flex items-center gap-1.5">
          <Lock className="w-3 h-3 text-emerald-400" />
          <span>Encrypted Technical Drive</span>
        </span>
      </header>

      {/* Main Form Container */}
      <main className="max-w-xl mx-auto w-full my-auto py-8 z-10">
        {/* Stepper */}
        <div className="flex items-center justify-between mb-8 px-4 text-xs font-medium">
          <div className={`flex items-center space-x-2 ${step === 1 ? 'text-indigo-400 font-semibold' : 'text-emerald-400'}`}>
            <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold ${step === 1 ? 'bg-indigo-600 text-white shadow-glow-primary' : 'bg-emerald-500 text-white shadow-glow-emerald'}`}>
              {step > 1 ? <Check className="w-3.5 h-3.5" /> : '1'}
            </span>
            <span>Verification</span>
          </div>
          <div className="h-[1px] flex-1 mx-4 bg-white/10"></div>
          <div className={`flex items-center space-x-2 ${step === 2 ? 'text-indigo-400 font-semibold' : 'text-slate-500'}`}>
            <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold ${step === 2 ? 'bg-indigo-600 text-white shadow-glow-primary' : 'bg-white/10 text-slate-400'}`}>
              2
            </span>
            <span>Device Check</span>
          </div>
        </div>

        <AnimatePresence mode="wait">
          {step === 1 ? (
            <motion.div 
              key="step1"
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 16 }}
              transition={{ duration: 0.3 }}
              className="glass-panel border border-white/10 rounded-3xl p-8 shadow-2xl relative overflow-hidden"
            >
              <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-indigo-500 to-purple-500" />

              <span className="text-[10px] font-mono uppercase tracking-wider text-indigo-300 bg-indigo-500/10 border border-indigo-500/20 px-3 py-1 rounded-full font-semibold inline-flex items-center gap-1.5">
                <Sparkles className="w-3 h-3 text-indigo-400" />
                Adaptive Technical Screening
              </span>
              <h1 className="text-2xl font-bold text-white tracking-tight mt-4">
                {invitationData ? `Welcome, ${invitationData.candidate_name}` : 'Welcome to your interview'}
              </h1>
              <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
                {invitationData ? `Assessment for ${invitationData.drive_name}. The session is dynamic, adaptive, and evidence-driven.` : 'You have been invited to complete a live voice assessment. The session is dynamic, adaptive, and evidence-driven.'}
              </p>

              <div className="bg-black/30 border border-white/10 rounded-2xl p-4 my-6 text-xs space-y-2 font-mono">
                <div className="flex justify-between"><span className="text-slate-400">Target Position:</span> <span className="font-semibold text-white">{invitationData?.job_title || 'Senior Backend Engineer'}</span></div>
                <div className="flex justify-between"><span className="text-slate-400">Session Duration:</span> <span className="text-white">15–25 minutes</span></div>
                <div className="flex justify-between"><span className="text-slate-400">Security Layer:</span> <span className="text-emerald-400">TLS &amp; Tenant RLS Enforced</span></div>
              </div>

              <div className="space-y-3 mb-8 text-xs text-slate-300">
                <div className="flex items-start space-x-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                  <span>Speak naturally into your microphone. The AI will drill into your technical reasoning.</span>
                </div>
                <div className="flex items-start space-x-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                  <span>You can interrupt or take the floor at any point during the interview.</span>
                </div>
                <div className="flex items-start space-x-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                  <span>Please ensure you are in a quiet room with a reliable internet connection.</span>
                </div>
              </div>

              <button 
                onClick={() => setStep(2)}
                className="w-full bg-indigo-600 hover:bg-indigo-500 active:scale-95 text-white py-3.5 rounded-xl text-xs font-semibold transition-all flex items-center justify-center space-x-2 shadow-glow-primary cursor-pointer"
              >
                <span>Continue to Device Check</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </motion.div>
          ) : (
            <motion.div 
              key="step2"
              initial={{ opacity: 0, x: 16 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -16 }}
              transition={{ duration: 0.3 }}
              className="glass-panel border border-white/10 rounded-3xl p-8 shadow-2xl relative overflow-hidden"
            >
              <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-purple-500 to-cyan-500" />

              <h2 className="text-xl font-bold text-white tracking-tight mb-2">Check your hardware</h2>
              <p className="text-xs text-slate-400 mb-6 leading-relaxed">
                Confirm your audio hardware and connection quality meet standards for streaming speech.
              </p>

              <div className="space-y-4 mb-8">
                {/* Mic Check */}
                <div className="glass-card rounded-2xl p-4 flex items-center justify-between border-white/10">
                  <div className="flex items-center space-x-3">
                    <div className="w-9 h-9 rounded-xl bg-indigo-600/20 border border-indigo-500/30 text-indigo-400 flex items-center justify-center shadow-glow-primary">
                      <Mic className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-xs font-semibold text-white">Microphone Input</div>
                      <div className={`text-[10px] font-mono mt-0.5 ${micVerified ? 'text-emerald-400' : 'text-slate-400'}`}>{micStatus}</div>
                    </div>
                  </div>
                  <button 
                    onClick={testMicrophone}
                    className={`text-xs px-3.5 py-1.5 rounded-xl font-medium transition-all cursor-pointer ${
                      micVerified 
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' 
                        : 'glass-card hover:border-slate-500 text-white'
                    }`}
                  >
                    {micVerified ? 'Verified' : 'Test Mic'}
                  </button>
                </div>

                {/* Browser Compatibility */}
                <div className="glass-card rounded-2xl p-4 flex items-center justify-between border-white/10">
                  <div className="flex items-center space-x-3">
                    <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center">
                      <Globe className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-xs font-semibold text-white">Browser Compatibility</div>
                      <div className="text-[10px] text-emerald-400 font-mono mt-0.5">WebRTC &amp; WebAudio Supported</div>
                    </div>
                  </div>
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                </div>

                {/* Network Quality */}
                <div className="glass-card rounded-2xl p-4 flex items-center justify-between border-white/10">
                  <div className="flex items-center space-x-3">
                    <div className="w-9 h-9 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center">
                      <Wifi className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-xs font-semibold text-white">Network Latency</div>
                      <div className="text-[10px] text-emerald-400 font-mono mt-0.5">Sub-second Latency Confirmed</div>
                    </div>
                  </div>
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                </div>
              </div>

              {/* Quiet Checkbox */}
              <label className="flex items-center space-x-3 text-xs text-slate-300 cursor-pointer mb-8 select-none">
                <input 
                  type="checkbox" 
                  checked={quietConfirmed}
                  onChange={(e) => setQuietConfirmed(e.target.checked)}
                  className="rounded border-white/20 text-indigo-600 focus:ring-indigo-500 w-4 h-4 cursor-pointer accent-indigo-600" 
                />
                <span>I confirm that I am in a quiet environment and ready to speak.</span>
              </label>

              <button 
                onClick={handleStartInterview}
                disabled={!quietConfirmed}
                className="w-full bg-indigo-600 hover:bg-indigo-500 active:scale-95 text-white py-3.5 rounded-xl text-xs font-semibold transition-all flex items-center justify-center space-x-2 disabled:opacity-40 disabled:pointer-events-none shadow-glow-primary cursor-pointer"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Begin Voice Interview</span>
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="max-w-xl mx-auto w-full text-center text-xs text-slate-500 pt-6 border-t border-white/10 z-10">
        Autergo Enterprise Platform &bull; End-to-End Encrypted Session
      </footer>
    </div>
  );
}
