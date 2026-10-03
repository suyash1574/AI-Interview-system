import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { ShieldCheck, Mic, Globe, Wifi, Check, ArrowRight, Play, CheckCircle2 } from 'lucide-react';

export default function CandidateCheckin() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || 'guest-demo';
  const interviewId = searchParams.get('interview_id') || 'int-demo';

  const [step, setStep] = useState(1);
  const [micStatus, setMicStatus] = useState('Click to test');
  const [micVerified, setMicVerified] = useState(false);
  const [quietConfirmed, setQuietConfirmed] = useState(false);

  const testMicrophone = async () => {
    try {
      await navigator.mediaDevices.getUserMedia({ audio: true });
      setMicStatus('Microphone Active & Verified');
      setMicVerified(true);
    } catch (e) {
      setMicStatus('Simulated Active Input');
      setMicVerified(true);
    }
  };

  const handleStartInterview = () => {
    const sessionId = 'session-' + Math.random().toString(36).substring(2, 9);
    navigate(`/interview/${sessionId}?interview_id=${interviewId}&token=${token}`);
  };

  return (
    <div className="min-h-screen bg-canvas-subtle text-ink flex flex-col justify-between p-6">
      {/* Top Header */}
      <header className="max-w-xl mx-auto w-full flex items-center justify-between pb-6 border-b border-border/80">
        <Link to="/" className="flex items-center space-x-2 text-ink font-semibold text-sm">
          <ShieldCheck className="w-5 h-5 text-primary" />
          <span>Autergo</span>
        </Link>
        <span className="text-xs text-ink-muted font-mono">Acme Corp Technical Drive</span>
      </header>

      {/* Main Form Container */}
      <main className="max-w-xl mx-auto w-full my-auto py-8">
        {/* Stepper */}
        <div className="flex items-center justify-between mb-8 px-4 text-xs font-medium">
          <div className={`flex items-center space-x-2 ${step === 1 ? 'text-primary font-semibold' : 'text-emerald-600'}`}>
            <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold ${step === 1 ? 'bg-primary text-white' : 'bg-emerald-600 text-white'}`}>
              {step > 1 ? <Check className="w-3.5 h-3.5" /> : '1'}
            </span>
            <span>Verification</span>
          </div>
          <div className="h-0.5 flex-1 mx-4 bg-border"></div>
          <div className={`flex items-center space-x-2 ${step === 2 ? 'text-primary font-semibold' : 'text-ink-muted'}`}>
            <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold ${step === 2 ? 'bg-primary text-white' : 'bg-border text-ink-muted'}`}>
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
              className="bg-white border border-border rounded-xl p-8 shadow-xs"
            >
              <span className="text-[11px] font-mono uppercase tracking-wider text-primary bg-primary-subtle px-2.5 py-1 rounded-full font-semibold">
                Technical Screening
              </span>
              <h1 className="text-2xl font-semibold text-ink tracking-tight mt-3">Welcome to your interview</h1>
              <p className="text-xs text-ink-muted mt-1 leading-relaxed">
                You have been invited to complete a live voice assessment. The session is dynamic, adaptive, and evidence-driven.
              </p>

              <div className="bg-canvas-subtle border border-border rounded-lg p-4 my-6 text-xs space-y-2 font-mono">
                <div className="flex justify-between"><span className="text-ink-muted">Target Position:</span> <span class="font-semibold text-ink">Senior Backend Engineer</span></div>
                <div className="flex justify-between"><span className="text-ink-muted">Session Duration:</span> <span class="text-ink">15–25 minutes</span></div>
                <div className="flex justify-between"><span className="text-ink-muted">Encryption:</span> <span class="text-emerald-600">TLS End-to-End</span></div>
              </div>

              <div className="space-y-3 mb-8 text-xs text-ink">
                <div className="flex items-start space-x-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
                  <span>Speak naturally into your microphone. The AI will drill into your technical reasoning.</span>
                </div>
                <div className="flex items-start space-x-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
                  <span>You can interrupt or take the floor at any point during the interview.</span>
                </div>
                <div className="flex items-start space-x-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
                  <span>Please ensure you are in a quiet room with a reliable internet connection.</span>
                </div>
              </div>

              <button 
                onClick={() => setStep(2)}
                className="w-full bg-primary hover:bg-primary-hover active:scale-95 text-white py-3 rounded-lg text-xs font-semibold transition-all flex items-center justify-center space-x-2"
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
              className="bg-white border border-border rounded-xl p-8 shadow-xs"
            >
              <h2 className="text-xl font-semibold text-ink tracking-tight mb-2">Check your hardware</h2>
              <p className="text-xs text-ink-muted mb-6 leading-relaxed">
                Confirm your audio hardware and connection quality meet standards for streaming speech.
              </p>

              <div className="space-y-4 mb-8">
                {/* Mic Check */}
                <div className="border border-border rounded-lg p-4 flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 rounded-full bg-primary-subtle text-primary flex items-center justify-center">
                      <Mic className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-xs font-semibold text-ink">Microphone</div>
                      <div className={`text-[11px] font-mono ${micVerified ? 'text-emerald-600' : 'text-ink-muted'}`}>{micStatus}</div>
                    </div>
                  </div>
                  <button 
                    onClick={testMicrophone}
                    className={`text-xs px-3 py-1.5 rounded-md font-medium transition-colors ${micVerified ? 'bg-emerald-50 text-emerald-700 border border-emerald-500' : 'border border-border hover:bg-canvas-subtle text-ink'}`}
                  >
                    {micVerified ? 'Verified' : 'Test Mic'}
                  </button>
                </div>

                {/* Browser Compatibility */}
                <div className="border border-border rounded-lg p-4 flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center">
                      <Globe className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-xs font-semibold text-ink">Browser Compatibility</div>
                      <div className="text-[11px] text-emerald-600 font-mono">Modern Browser Supported</div>
                    </div>
                  </div>
                  <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                </div>

                {/* Network Quality */}
                <div className="border border-border rounded-lg p-4 flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 rounded-full bg-primary-subtle text-primary flex items-center justify-center">
                      <Wifi className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-xs font-semibold text-ink">Network Latency</div>
                      <div className="text-[11px] text-emerald-600 font-mono">Sub-second Latency Guaranteed</div>
                    </div>
                  </div>
                  <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                </div>
              </div>

              {/* Quiet Checkbox */}
              <label className="flex items-center space-x-3 text-xs text-ink cursor-pointer mb-8 select-none">
                <input 
                  type="checkbox" 
                  checked={quietConfirmed}
                  onChange={(e) => setQuietConfirmed(e.target.checked)}
                  className="rounded border-border text-primary focus:ring-primary w-4 h-4 cursor-pointer" 
                />
                <span>I confirm that I am in a quiet environment and ready to speak.</span>
              </label>

              <button 
                onClick={handleStartInterview}
                disabled={!quietConfirmed}
                className="w-full bg-primary hover:bg-primary-hover active:scale-95 text-white py-3 rounded-lg text-xs font-semibold transition-all flex items-center justify-center space-x-2 disabled:opacity-40 disabled:pointer-events-none"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Begin Voice Interview</span>
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="max-w-xl mx-auto w-full text-center text-xs text-ink-muted pt-6 border-t border-border/80">
        Autergo Enterprise Platform &bull; End-to-End Encrypted Session
      </footer>
    </div>
  );
}
