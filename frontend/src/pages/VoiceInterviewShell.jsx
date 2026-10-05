import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useParams, useSearchParams, useNavigate, Link } from 'react-router-dom';
import { 
  ShieldCheck, 
  Mic, 
  MicOff, 
  Hand, 
  Send, 
  CheckCircle2, 
  Lock, 
  AlertCircle,
  Radio,
  Volume2,
  Sparkles,
  Bot,
  User,
  Clock,
  Zap,
  Activity,
  ChevronRight
} from 'lucide-react';
import { LiveKitRoom, RoomAudioRenderer } from '@livekit/components-react';

export default function VoiceInterviewShell() {
  const { sessionId: paramSessionId } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const sessionId = paramSessionId || 'session-' + Math.random().toString(36).substring(2, 9);
  const interviewId = searchParams.get('interview_id') || 'int-demo';

  const [connected, setConnected] = useState(false);
  const [currentStage, setCurrentStage] = useState('INTRODUCTION');
  const [competency, setCompetency] = useState('SYSTEM DESIGN & PROBLEM SOLVING');
  const [aiPrompt, setAiPrompt] = useState('Hello! Welcome to your Autergo technical interview. Please briefly introduce yourself and your background.');
  const [transcript, setTranscript] = useState([
    { speaker: 'AI', text: 'Hello! Welcome to your Autergo technical interview. Please briefly introduce yourself and your background.', time: '00:01' }
  ]);
  const [currentState, setCurrentState] = useState('Listening');
  const [isMuted, setIsMuted] = useState(false);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [manualInput, setManualInput] = useState('');
  const [showCompleteModal, setShowCompleteModal] = useState(false);
  const [integrityNotice, setIntegrityNotice] = useState(null);
  const [livekitToken, setLivekitToken] = useState(searchParams.get('livekit_token') || '');
  const livekitUrl = import.meta.env?.VITE_LIVEKIT_URL || 'wss://livekit.autergo.com';

  const wsRef = useRef(null);
  const transcriptBottomRef = useRef(null);

  const stagesList = [
    'INIT',
    'INTRODUCTION',
    'CORE_BACKGROUND',
    'SYSTEM_DESIGN',
    'DEEP_DIVE',
    'INCIDENT_RESPONSE',
    'SUMMARY',
    'WRAP_UP'
  ];

  // Auto-fetch LiveKit token if room is configured
  useEffect(() => {
    async function fetchLiveKitToken() {
      if (!livekitToken) {
        try {
          const res = await fetch('/api/v1/sessions/livekit-token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              room_name: `interview-${interviewId}`,
              participant_name: 'Candidate',
              participant_identity: `cand-${sessionId}`
            })
          });
          if (res.ok) {
            const data = await res.json();
            if (data.token) setLivekitToken(data.token);
          }
        } catch (e) {
          console.debug('LiveKit token auto-fetch fallback:', e);
        }
      }
    }
    fetchLiveKitToken();
  }, [interviewId, sessionId, livekitToken]);

  // Timer
  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedSeconds((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Auto-scroll transcript
  useEffect(() => {
    transcriptBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [transcript]);

  const formatTimer = (secs) => {
    const m = String(Math.floor(secs / 60)).padStart(2, '0');
    const s = String(secs % 60).padStart(2, '0');
    return `${m}:${s}`;
  };

  // WebSocket Connection
  useEffect(() => {
    const loc = window.location;
    const wsProtocol = loc.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = loc.port === '5173' ? `${loc.hostname}:8000` : loc.host;
    const wsUrl = `${wsProtocol}//${host}/api/v1/realtime/interview/${sessionId}?interview_id=${interviewId}`;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'ai_response') {
          setAiPrompt(msg.text);
          setTranscript((prev) => [...prev, { 
            speaker: 'AI', 
            text: msg.text,
            time: formatTimer(elapsedSeconds)
          }]);
          setCurrentState('AI Speaking');
        } else if (msg.type === 'transcript_partial') {
          setTranscript((prev) => [...prev, { 
            speaker: 'CANDIDATE', 
            text: msg.text,
            time: formatTimer(elapsedSeconds)
          }]);
          setCurrentState('Candidate Speaking');
        } else if (msg.type === 'state_change') {
          setCurrentStage(msg.new_state);
          if (msg.competency) setCompetency(msg.competency);
        } else if (msg.type === 'interrupted') {
          setCurrentState('Interrupted');
        } else if (msg.type === 'complete') {
          setShowCompleteModal(true);
        }
      } catch (err) {
        console.error(err);
      }
    };

    ws.onclose = () => {
      setConnected(false);
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [sessionId, interviewId, elapsedSeconds]);

  // Candidate Integrity Telemetry Monitoring
  useEffect(() => {
    const reportTelemetry = async (eventType, severity, meta = {}) => {
      try {
        await fetch(`/api/v1/interviews/${interviewId}/telemetry`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            event_type: eventType,
            severity: severity,
            metadata: {
              ...meta,
              client_timestamp: new Date().toISOString(),
              elapsed_seconds: elapsedSeconds
            }
          })
        });
      } catch (e) {
        console.warn('Telemetry dispatch error:', e);
      }
    };

    const handleVisibilityChange = () => {
      if (document.hidden) {
        reportTelemetry('TAB_SWITCH', 'MEDIUM', { reason: 'visibility_hidden' });
        setIntegrityNotice('Tab switch detected. System telemetry is actively recording.');
        setTimeout(() => setIntegrityNotice(null), 3500);
      }
    };

    const handlePaste = (e) => {
      reportTelemetry('COPY_PASTE', 'MEDIUM', { action: 'paste', length: e.clipboardData?.getData('text')?.length || 0 });
      setIntegrityNotice('Clipboard paste detected and logged for recruiter review.');
      setTimeout(() => setIntegrityNotice(null), 4000);
    };

    const handleCopy = () => {
      reportTelemetry('COPY_PASTE', 'LOW', { action: 'copy' });
    };

    const handleFullscreen = () => {
      if (!document.fullscreenElement) {
        reportTelemetry('FULLSCREEN_EXIT', 'MEDIUM', { reason: 'user_exit' });
      }
    };

    const handleWindowBlur = () => {
      reportTelemetry('WINDOW_BLUR', 'LOW', { reason: 'window_focus_lost' });
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('blur', handleWindowBlur);
    window.addEventListener('paste', handlePaste);
    window.addEventListener('copy', handleCopy);
    document.addEventListener('fullscreenchange', handleFullscreen);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('blur', handleWindowBlur);
      window.removeEventListener('paste', handlePaste);
      window.removeEventListener('copy', handleCopy);
      document.removeEventListener('fullscreenchange', handleFullscreen);
    };
  }, [interviewId, elapsedSeconds]);

  const sendCandidateAnswer = (textToSend) => {
    const text = textToSend || manualInput;
    if (!text.trim() || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;

    wsRef.current.send(JSON.stringify({
      type: 'candidate_answer',
      text: text.trim()
    }));
    setTranscript((prev) => [...prev, {
      speaker: 'CANDIDATE',
      text: text.trim(),
      time: formatTimer(elapsedSeconds)
    }]);
    setManualInput('');
    setCurrentState('Synthesizing Response');
  };

  const handleInterrupt = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'interrupt', timestamp: Date.now() }));
      setCurrentState('Interrupted');
    }
  };

  const handleFinish = () => {
    if (window.confirm('Are you ready to submit your interview for multi-agent evaluation?')) {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'finish' }));
      }
      setShowCompleteModal(true);
    }
  };

  // State visuals configuration
  const getStateColors = () => {
    switch (currentState) {
      case 'AI Speaking':
        return {
          glow: 'from-indigo-500/30 via-purple-500/20 to-cyan-500/10',
          ring: 'border-indigo-400/40',
          badge: 'bg-indigo-500/15 border-indigo-500/30 text-indigo-300',
          dot: 'bg-indigo-400',
          text: 'AI Speaking'
        };
      case 'Candidate Speaking':
        return {
          glow: 'from-emerald-500/30 via-teal-500/20 to-cyan-500/10',
          ring: 'border-emerald-400/40',
          badge: 'bg-emerald-500/15 border-emerald-500/30 text-emerald-300',
          dot: 'bg-emerald-400',
          text: 'Listening to Candidate'
        };
      case 'Synthesizing Response':
        return {
          glow: 'from-amber-500/30 via-purple-500/20 to-indigo-500/10',
          ring: 'border-amber-400/40',
          badge: 'bg-amber-500/15 border-amber-500/30 text-amber-300',
          dot: 'bg-amber-400',
          text: 'Synthesizing with Groq LLM...'
        };
      case 'Interrupted':
        return {
          glow: 'from-rose-500/30 via-amber-500/20 to-indigo-500/10',
          ring: 'border-rose-400/40',
          badge: 'bg-rose-500/15 border-rose-500/30 text-rose-300',
          dot: 'bg-rose-400',
          text: 'Candidate Interrupted'
        };
      default:
        return {
          glow: 'from-indigo-500/20 via-slate-500/10 to-transparent',
          ring: 'border-indigo-500/20',
          badge: 'bg-slate-800/60 border-white/10 text-slate-300',
          dot: 'bg-slate-400',
          text: 'Mic Active &bull; Ready'
        };
    }
  };

  const stateStyle = getStateColors();

  // 24-bar visualizer heights generator
  const visualizerBars = [
    18, 32, 48, 24, 64, 40, 72, 85, 96, 70, 52, 80,
    90, 68, 55, 78, 62, 45, 74, 58, 36, 42, 28, 16
  ];

  const shellContent = (
    <div className="h-screen w-screen bg-[#07090e] text-[#f8fafc] flex flex-col justify-between overflow-hidden select-none font-sans relative mesh-bg">
      {/* Ambient background glow orbs */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-gradient-to-tr from-indigo-600/15 via-purple-600/10 to-cyan-500/10 rounded-full blur-[120px] pointer-events-none -z-10" />
      <div className="absolute bottom-10 left-1/4 w-[400px] h-[200px] bg-blue-600/10 rounded-full blur-[100px] pointer-events-none -z-10" />

      {/* Top Glass Navigation Bar */}
      <header className="h-16 border-b border-white/10 px-6 flex items-center justify-between glass-panel z-20">
        <div className="flex items-center space-x-3">
          <Link to="/" className="flex items-center gap-2 group">
            <div className="w-8 h-8 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 group-hover:scale-105 transition-transform shadow-glow-primary">
              <ShieldCheck className="w-4 h-4 text-indigo-400" />
            </div>
            <div>
              <span className="text-sm font-semibold tracking-tight text-white flex items-center gap-1.5">
                Autergo <span className="text-[10px] text-indigo-400 font-mono font-medium px-1.5 py-0.2 rounded bg-indigo-500/10 border border-indigo-500/20">STUDIO</span>
              </span>
            </div>
          </Link>
          <span className="text-white/20 text-xs">/</span>
          <span className="text-xs text-slate-400 font-medium font-mono hidden sm:inline">Senior Technical Screening</span>
        </div>

        {/* Dynamic Multi-Stage Linear Progression Bar */}
        <div className="hidden lg:flex items-center space-x-1.5 bg-black/40 border border-white/10 px-3.5 py-1.5 rounded-full text-xs shadow-inner">
          {stagesList.slice(0, 6).map((stage, idx) => {
            const isCurrent = stage.toLowerCase() === currentStage.toLowerCase() || (idx === 1 && currentStage === 'INTRODUCTION');
            return (
              <React.Fragment key={stage}>
                <div className={`flex items-center space-x-1.5 px-2 py-0.5 rounded-full transition-all ${
                  isCurrent 
                    ? 'bg-indigo-500/20 border border-indigo-500/40 text-indigo-300 font-semibold' 
                    : 'text-slate-500 font-mono text-[10px]'
                }`}>
                  <span className={`w-1.5 h-1.5 rounded-full ${isCurrent ? 'bg-indigo-400 animate-ping' : 'bg-slate-700'}`} />
                  <span className="uppercase text-[10px] tracking-wider">{stage.replace('_', ' ')}</span>
                </div>
                {idx < 5 && <span className="text-white/15 text-[10px]">&bull;</span>}
              </React.Fragment>
            );
          })}
        </div>

        {/* Protocol & Duration Telemetry */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 bg-white/5 border border-white/10 px-3 py-1 rounded-full text-xs font-mono">
            {livekitToken ? (
              <span className="text-emerald-400 flex items-center gap-1.5 font-medium">
                <Volume2 className="w-3.5 h-3.5 animate-pulse" />
                <span>LIVEKIT WEBRTC</span>
              </span>
            ) : (
              <span className="text-cyan-400 flex items-center gap-1.5 font-medium">
                <Radio className="w-3.5 h-3.5 animate-pulse" />
                <span>{connected ? 'AUDIO WS STREAM' : 'LOCAL SIM'}</span>
              </span>
            )}
            <span className="text-white/20">|</span>
            <div className="flex items-center gap-1 text-slate-300 font-mono">
              <Clock className="w-3 h-3 text-slate-400" />
              <span>{formatTimer(elapsedSeconds)}</span>
            </div>
          </div>
        </div>
      </header>

      {/* Integrity Notice Alert Banner */}
      <AnimatePresence>
        {integrityNotice && (
          <motion.div
            initial={{ opacity: 0, y: -16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -16 }}
            className="bg-amber-950/90 border-b border-amber-600/50 px-4 py-2 flex items-center justify-center space-x-2 text-xs text-amber-200 z-30 backdrop-blur-md"
          >
            <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
            <span className="font-mono">{integrityNotice}</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Studio Viewport */}
      <main className="flex-1 flex flex-col items-center justify-between px-4 py-4 max-w-4xl mx-auto w-full relative z-10 overflow-hidden">
        
        {/* Dynamic Question / Topic Context Card */}
        <motion.div 
          key={aiPrompt}
          initial={{ opacity: 0, y: -12, scale: 0.98 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
          className="w-full glass-panel border border-white/10 rounded-2xl p-6 text-center shadow-2xl relative overflow-hidden"
        >
          {/* Subtle top indicator bar */}
          <div className="absolute top-0 inset-x-0 h-[2px] bg-gradient-to-r from-transparent via-indigo-500 to-transparent opacity-80" />

          <div className="flex items-center justify-center gap-2 mb-3">
            <span className="inline-flex items-center gap-1.5 text-[11px] font-mono tracking-wider text-indigo-300 bg-indigo-500/15 border border-indigo-500/30 px-3 py-1 rounded-full uppercase font-medium">
              <Sparkles className="w-3 h-3 text-indigo-400" />
              {competency}
            </span>
          </div>

          <h2 className="text-lg md:text-xl font-medium text-white leading-relaxed tracking-tight max-w-2xl mx-auto">
            "{aiPrompt}"
          </h2>
        </motion.div>

        {/* Centerpiece: AI Holographic Audio Orb & Visualizer */}
        <div className="flex flex-col items-center justify-center my-auto relative py-2">
          {/* Outer Ripple Rings */}
          <div className="relative flex items-center justify-center w-48 h-48">
            <motion.div 
              animate={{ 
                scale: currentState === 'AI Speaking' || currentState === 'Candidate Speaking' ? [1, 1.25, 1] : [1, 1.08, 1],
                opacity: currentState === 'AI Speaking' || currentState === 'Candidate Speaking' ? [0.4, 0.1, 0.4] : [0.2, 0.05, 0.2]
              }}
              transition={{ duration: 2.2, repeat: Infinity, ease: 'easeInOut' }}
              className={`absolute inset-0 rounded-full border border-indigo-500/30 bg-gradient-to-tr ${stateStyle.glow} blur-xl`}
            />

            <motion.div 
              animate={{ 
                scale: currentState === 'AI Speaking' || currentState === 'Candidate Speaking' ? [1, 1.15, 1] : [1, 1.04, 1],
                rotate: [0, 180, 360]
              }}
              transition={{ 
                scale: { duration: 1.8, repeat: Infinity, ease: 'easeInOut' },
                rotate: { duration: 20, repeat: Infinity, ease: 'linear' }
              }}
              className={`absolute inset-3 rounded-full border border-dashed ${stateStyle.ring}`}
            />

            {/* Core Glowing Sphere */}
            <div className="relative w-28 h-28 rounded-full bg-gradient-to-br from-indigo-900/80 via-slate-900/90 to-black/90 border border-white/20 flex flex-col items-center justify-center shadow-2xl backdrop-blur-md overflow-hidden">
              <div className="absolute inset-0 bg-radial from-indigo-500/20 to-transparent" />
              
              <motion.div
                animate={
                  currentState === 'AI Speaking' 
                    ? { scale: [1, 1.12, 1], rotate: [0, 5, -5, 0] }
                    : currentState === 'Synthesizing Response'
                    ? { rotate: 360 }
                    : { scale: [1, 1.05, 1] }
                }
                transition={{ duration: currentState === 'Synthesizing Response' ? 1.5 : 2.5, repeat: Infinity }}
                className="relative z-10 text-indigo-400"
              >
                <Bot className="w-10 h-10 drop-shadow-[0_0_12px_rgba(99,102,241,0.6)]" />
              </motion.div>
            </div>
          </div>

          {/* 24-Band Dynamic Audio Frequency Equalizer */}
          <div className="flex items-center justify-center gap-1 h-12 mt-3 px-6 py-1 rounded-full bg-black/30 border border-white/5 backdrop-blur-md">
            {visualizerBars.map((height, i) => {
              const isActive = (currentState === 'AI Speaking' || currentState === 'Candidate Speaking') && !isMuted;
              return (
                <motion.div
                  key={i}
                  animate={
                    isActive
                      ? { 
                          height: [10, height, 14, height * 0.7, 10],
                          backgroundColor: ['#6366f1', '#a855f7', '#06b6d4', '#6366f1']
                        }
                      : { height: 6, backgroundColor: '#334155' }
                  }
                  transition={{ 
                    duration: 0.7 + (i % 5) * 0.12, 
                    repeat: Infinity, 
                    ease: 'easeInOut',
                    delay: (i % 4) * 0.08
                  }}
                  className="w-1.5 rounded-full visualizer-bar"
                  style={{ height: 6 }}
                />
              );
            })}
          </div>

          {/* Realtime Reactive Audio Status Pill */}
          <div className="mt-3 flex items-center">
            <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono border backdrop-blur-md transition-all ${stateStyle.badge}`}>
              <span className={`w-2 h-2 rounded-full ${stateStyle.dot} animate-pulse`} />
              <span>{stateStyle.text}</span>
            </span>
          </div>
        </div>

        {/* Live Conversation Transcript Feed */}
        <div className="w-full glass-panel border border-white/10 rounded-2xl p-4 max-h-48 overflow-y-auto font-sans text-xs space-y-3 shadow-inner">
          <div className="text-[10px] font-mono text-slate-500 uppercase tracking-wider flex items-center justify-between pb-1 border-b border-white/5">
            <span>Verified Transcript Feed</span>
            <span>Sub-second Latency Sync</span>
          </div>

          <div className="space-y-2.5">
            {transcript.map((item, idx) => (
              <motion.div 
                key={idx}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-3 p-2.5 rounded-xl border ${
                  item.speaker === 'AI' 
                    ? 'bg-indigo-500/5 border-indigo-500/20' 
                    : 'bg-emerald-500/5 border-emerald-500/20'
                }`}
              >
                <div className={`w-6 h-6 rounded-lg flex items-center justify-center shrink-0 text-xs font-semibold ${
                  item.speaker === 'AI' 
                    ? 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30' 
                    : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                }`}>
                  {item.speaker === 'AI' ? <Bot className="w-3.5 h-3.5" /> : <User className="w-3.5 h-3.5" />}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-0.5">
                    <span className={`font-mono text-[11px] font-semibold ${
                      item.speaker === 'AI' ? 'text-indigo-400' : 'text-emerald-400'
                    }`}>
                      {item.speaker === 'AI' ? 'Autergo Voice AI' : 'Candidate Jane Doe'}
                    </span>
                    <span className="text-[10px] text-slate-500 font-mono">{item.time || 'now'}</span>
                  </div>
                  <p className="text-slate-200 leading-relaxed text-xs">
                    {item.text}
                  </p>
                </div>
              </motion.div>
            ))}
            <div ref={transcriptBottomRef} />
          </div>
        </div>

        {/* Manual Input Fallback Strip */}
        <div className="w-full mt-3 flex items-center space-x-2">
          <div className="relative flex-1">
            <input 
              type="text" 
              value={manualInput}
              onChange={(e) => setManualInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendCandidateAnswer()}
              placeholder="Speak naturally via microphone, or type your answer here..." 
              className="w-full bg-slate-900/60 border border-white/10 rounded-xl px-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/40 transition-all font-mono"
            />
          </div>
          <button 
            onClick={() => sendCandidateAnswer()}
            className="bg-indigo-600 hover:bg-indigo-500 active:scale-95 text-white px-5 py-2.5 rounded-xl text-xs font-medium transition-all flex items-center gap-1.5 shadow-glow-primary cursor-pointer shrink-0"
          >
            <span>Send</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </div>
      </main>

      {/* Floating Bottom Control Deck */}
      <footer className="h-20 border-t border-white/10 px-8 flex items-center justify-between glass-panel z-20">
        {/* Candidate Profile Pill */}
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600/30 to-purple-600/30 border border-white/15 flex items-center justify-center font-medium text-xs text-white shadow-inner">
            JD
          </div>
          <div>
            <div className="text-xs font-semibold text-white">Candidate Jane Doe</div>
            <div className="text-[10px] text-slate-400 font-mono">Session: {sessionId.substring(0, 10)}...</div>
          </div>
        </div>

        {/* Center Interactive Buttons */}
        <div className="flex items-center space-x-3">
          {/* Mute Button */}
          <button 
            onClick={() => setIsMuted(!isMuted)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-medium transition-all border cursor-pointer ${
              isMuted 
                ? 'bg-rose-500/10 border-rose-500/40 text-rose-400 shadow-[0_0_15px_rgba(244,63,94,0.3)]' 
                : 'bg-white/5 border-white/10 hover:border-slate-500 text-white hover:bg-white/10'
            }`}
          >
            {isMuted ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4 text-emerald-400" />}
            <span>{isMuted ? 'Microphone Muted' : 'Mute Mic'}</span>
          </button>

          {/* Barge-in Interrupt Button */}
          <button 
            onClick={handleInterrupt}
            className="flex items-center space-x-2 bg-amber-500/10 border border-amber-500/30 hover:border-amber-500/60 hover:bg-amber-500/20 px-4 py-2 rounded-xl text-xs font-medium transition-all text-amber-300 active:scale-95 cursor-pointer shadow-[0_0_15px_rgba(245,158,11,0.15)]"
          >
            <Hand className="w-4 h-4" />
            <span>Interrupt AI (Barge-in)</span>
          </button>

          {/* Finish Button */}
          <button 
            onClick={handleFinish}
            className="bg-rose-600/20 border border-rose-500/40 hover:bg-rose-600/30 text-rose-200 px-4 py-2 rounded-xl text-xs font-medium transition-all active:scale-95 cursor-pointer"
          >
            End Interview
          </button>
        </div>

        {/* Security & Isolation Metric */}
        <div className="flex items-center space-x-2 text-slate-400 text-xs font-mono">
          <Lock className="w-3.5 h-3.5 text-indigo-400" />
          <span className="hidden sm:inline">256-Bit TLS &bull; RLS Encrypted</span>
        </div>
      </footer>

      {/* Completion Modal Overlay */}
      <AnimatePresence>
        {showCompleteModal && (
          <div className="fixed inset-0 bg-black/85 backdrop-blur-xl flex items-center justify-center z-50 p-4">
            <motion.div 
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              className="glass-panel border border-white/15 rounded-3xl p-8 max-w-md w-full text-center shadow-2xl relative overflow-hidden"
            >
              <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-emerald-500 via-indigo-500 to-cyan-500" />
              
              <div className="w-14 h-14 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl flex items-center justify-center mx-auto mb-4 text-emerald-400 shadow-glow-emerald">
                <CheckCircle2 className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2 tracking-tight">Interview Successfully Submitted</h3>
              <p className="text-xs text-slate-400 leading-relaxed mb-6">
                Your vocal responses and integrity telemetry have been dispatched to the multi-agent consensus pipeline. The evaluation report will be compiled within 60 seconds.
              </p>
              
              <div className="bg-black/40 border border-white/10 rounded-2xl p-4 mb-6 text-left text-xs font-mono space-y-2">
                <div className="flex justify-between text-slate-400">
                  <span>Session Duration:</span> 
                  <span className="text-white font-semibold">{formatTimer(elapsedSeconds)}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Stages Completed:</span> 
                  <span className="text-emerald-400 font-semibold">All 9 Stages Passed</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Evaluation Engine:</span> 
                  <span className="text-indigo-400 font-semibold">Groq NAT Multi-Agent</span>
                </div>
              </div>

              <div className="space-y-2">
                <button 
                  onClick={() => navigate(`/reports/${interviewId}`)}
                  className="w-full bg-indigo-600 hover:bg-indigo-500 active:scale-95 text-white py-3 rounded-xl text-xs font-semibold transition-all shadow-glow-primary cursor-pointer flex items-center justify-center gap-1.5"
                >
                  <span>View Evaluation Scorecard</span>
                  <ChevronRight className="w-4 h-4" />
                </button>
                <button 
                  onClick={() => navigate('/')}
                  className="w-full bg-white/5 hover:bg-white/10 active:scale-95 text-slate-300 py-2.5 rounded-xl text-xs font-medium transition-all cursor-pointer"
                >
                  Return to Home
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );

  if (livekitToken && livekitUrl && !livekitToken.includes('placeholder')) {
    return (
      <LiveKitRoom
        serverUrl={livekitUrl}
        token={livekitToken}
        connect={true}
        audio={!isMuted}
        video={false}
      >
        <RoomAudioRenderer />
        {shellContent}
      </LiveKitRoom>
    );
  }

  return shellContent;
}
