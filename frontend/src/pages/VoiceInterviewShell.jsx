import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
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
  Volume2
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
    { speaker: 'AI', text: 'Hello! Welcome to your Autergo technical interview. Please briefly introduce yourself and your background.' }
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

  // WebSocket Connection
  useEffect(() => {
    const loc = window.location;
    const wsProtocol = loc.protocol === 'https:' ? 'wss:' : 'ws:';
    // When running Vite dev server on port 5173, point directly to FastAPI backend port 8000
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
          setTranscript((prev) => [...prev, { speaker: 'AI', text: msg.text }]);
          setCurrentState('AI Speaking');
        } else if (msg.type === 'transcript_partial') {
          setTranscript((prev) => [...prev, { speaker: 'CANDIDATE', text: msg.text }]);
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
  }, [sessionId, interviewId]);

  // Candidate Integrity Telemetry Monitoring (Tab Switch & Window Blur)
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
    setManualInput('');
    setCurrentState('Synthesizing Response');
  };

  const handleInterrupt = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'interrupt', timestamp: Date.now() }));
    }
  };

  const handleFinish = () => {
    if (window.confirm('Are you ready to submit your interview for scoring?')) {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'finish' }));
      } else {
        setShowCompleteModal(true);
      }
    }
  };

  const formatTimer = (secs) => {
    const m = String(Math.floor(secs / 60)).padStart(2, '0');
    const s = String(secs % 60).padStart(2, '0');
    return `${m}:${s}`;
  };

  const shellContent = (
    <div className="h-screen w-screen bg-dark-base text-dark-ink flex flex-col justify-between overflow-hidden select-none font-sans">
      {/* Top Bar */}
      <header className="h-14 border-b border-dark-border px-6 flex items-center justify-between bg-dark-surface/50 backdrop-blur-md">
        <div className="flex items-center space-x-3">
          <span className="text-sm font-semibold tracking-tight text-white flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-primary-ondark" />
            <span>Autergo</span>
          </span>
          <span className="text-dark-border text-xs">/</span>
          <span className="text-xs text-dark-muted font-medium font-mono">Senior Backend Screening</span>
        </div>

        {/* State Stage Pill */}
        <div className="flex items-center space-x-2 bg-dark-surface border border-dark-border px-3.5 py-1 rounded-full text-xs shadow-xs">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="text-dark-muted font-mono uppercase text-[11px] tracking-wider">STAGE:</span>
          <span className="font-semibold text-white tracking-wide">{currentStage}</span>
        </div>

        {/* Status indicator */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-1.5 text-xs text-emerald-400 font-mono">
            {livekitToken ? (
              <>
                <Volume2 className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
                <span>LIVEKIT WEBRTC</span>
              </>
            ) : (
              <>
                <Radio className="w-3.5 h-3.5 animate-pulse" />
                <span>{connected ? 'AUDIO WS STREAM' : 'LOCAL SIM'}</span>
              </>
            )}
          </div>
          <span className="text-dark-muted text-xs font-mono pl-3">{formatTimer(elapsedSeconds)}</span>
        </div>
      </header>

      {/* Integrity Notice Banner */}
      <AnimatePresence>
        {integrityNotice && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="bg-amber-950/80 border-b border-amber-800/60 px-4 py-2 flex items-center justify-center space-x-2 text-xs text-amber-200 z-20"
          >
            <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
            <span>{integrityNotice}</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Center Area */}
      <main className="flex-1 flex flex-col items-center justify-center px-4 max-w-3xl mx-auto w-full relative">
        {/* Question Context Card */}
        <motion.div 
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full bg-dark-surface/70 border border-dark-border rounded-xl p-6 mb-6 text-center backdrop-blur-sm shadow-xl"
        >
          <span className="inline-block text-[11px] font-mono tracking-wider text-primary-ondark bg-primary/20 px-3 py-0.5 rounded-full mb-3 uppercase">
            {competency}
          </span>
          <h2 className="text-lg md:text-xl font-medium text-white leading-relaxed tracking-tight">
            "{aiPrompt}"
          </h2>
        </motion.div>

        {/* Visualizer Waveform */}
        <div className="flex flex-col items-center justify-center my-4">
          <div className="flex items-center justify-center space-x-2 h-14 mb-3">
            {[24, 38, 52, 38, 24].map((h, i) => (
              <motion.div
                key={i}
                animate={isMuted ? { height: 10 } : { height: [12, h, 16, h * 0.8, 12] }}
                transition={{ duration: 0.8 + i * 0.1, repeat: Infinity, ease: 'easeInOut' }}
                className={`w-1 rounded-full ${isMuted ? 'bg-dark-muted' : 'bg-primary-ondark'}`}
              />
            ))}
          </div>
          <div className="flex items-center space-x-2 text-xs font-mono text-dark-muted">
            <span className="w-2 h-2 rounded-full bg-primary-ondark animate-ping"></span>
            <span>{currentState} &bull; Microphone active</span>
          </div>
        </div>

        {/* Realtime Captions Panel */}
        <div className="w-full max-h-44 overflow-y-auto bg-dark-surface/30 border border-dark-border/60 rounded-lg p-4 font-mono text-xs space-y-2.5 shadow-inner">
          {transcript.map((item, idx) => (
            <div key={idx} className="flex gap-2">
              <span className={`font-semibold shrink-0 ${item.speaker === 'AI' ? 'text-primary-ondark' : 'text-emerald-400'}`}>
                [{item.speaker}]:
              </span>
              <span className="text-white leading-relaxed">{item.text}</span>
            </div>
          ))}
          <div ref={transcriptBottomRef} />
        </div>

        {/* Manual Speech Fallback Bar */}
        <div className="w-full mt-4 flex items-center space-x-2">
          <input 
            type="text" 
            value={manualInput}
            onChange={(e) => setManualInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendCandidateAnswer()}
            placeholder="Speak or type your technical answer here..." 
            className="flex-1 bg-dark-surface border border-dark-border rounded-lg px-4 py-2.5 text-xs text-white placeholder-dark-muted focus:outline-none focus:border-primary transition-colors font-mono"
          />
          <button 
            onClick={() => sendCandidateAnswer()}
            className="bg-primary hover:bg-primary-hover active:scale-95 text-white px-4 py-2.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5"
          >
            <span>Send</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </div>
      </main>

      {/* Bottom Deck Controls */}
      <footer className="h-20 border-t border-dark-border px-8 flex items-center justify-between bg-dark-surface/60 backdrop-blur-md">
        {/* Candidate Badge */}
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-full bg-dark-surface border border-dark-border flex items-center justify-center font-medium text-xs text-white">
            JD
          </div>
          <div>
            <div className="text-xs font-semibold text-white">Candidate Jane Doe</div>
            <div className="text-[11px] text-dark-muted font-mono">Session ID: {sessionId.substring(0, 10)}...</div>
          </div>
        </div>

        {/* Center Controls */}
        <div className="flex items-center space-x-3">
          <button 
            onClick={() => setIsMuted(!isMuted)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-full text-xs font-medium transition-all border ${
              isMuted ? 'bg-red-500/10 border-red-500/40 text-red-400' : 'bg-dark-surface border-dark-border hover:border-dark-muted text-white'
            }`}
          >
            {isMuted ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4 text-emerald-400" />}
            <span>{isMuted ? 'Unmute Mic' : 'Mute Mic'}</span>
          </button>

          <button 
            onClick={handleInterrupt}
            className="flex items-center space-x-2 bg-dark-surface border border-dark-border hover:border-amber-500/50 px-4 py-2 rounded-full text-xs font-medium transition-all text-amber-400 active:scale-95"
          >
            <Hand className="w-4 h-4" />
            <span>Interrupt AI</span>
          </button>

          <button 
            onClick={handleFinish}
            className="bg-red-950/40 border border-red-800/60 hover:bg-red-900/60 text-red-200 px-4 py-2 rounded-full text-xs font-medium transition-all active:scale-95"
          >
            End Interview
          </button>
        </div>

        <div className="flex items-center space-x-1.5 text-dark-muted text-xs font-mono">
          <Lock className="w-3.5 h-3.5" />
          <span>TLS Encrypted</span>
        </div>
      </footer>

      {/* Complete Modal Overlay */}
      <AnimatePresence>
        {showCompleteModal && (
          <div className="fixed inset-0 bg-dark-base/90 backdrop-blur-md flex items-center justify-center z-50 p-4">
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-dark-surface border border-dark-border rounded-2xl p-8 max-w-md w-full text-center shadow-2xl"
            >
              <div className="w-12 h-12 bg-emerald-500/10 border border-emerald-500/30 rounded-full flex items-center justify-center mx-auto mb-4 text-emerald-400">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2 tracking-tight">Interview Submitted</h3>
              <p className="text-xs text-dark-muted leading-relaxed mb-6">
                Your voice responses have been encrypted and submitted to the evaluation engine. The recruiting team will review the evidence-backed scorecard shortly.
              </p>
              <div className="bg-dark-base/60 border border-dark-border rounded-lg p-3.5 mb-6 text-left text-xs font-mono space-y-1.5">
                <div className="flex justify-between text-dark-muted"><span>Session Duration:</span> <span className="text-white">{formatTimer(elapsedSeconds)}</span></div>
                <div className="flex justify-between text-dark-muted"><span>Questions Completed:</span> <span className="text-emerald-400">10 / 10 Stages</span></div>
                <div className="flex justify-between text-dark-muted"><span>Pipeline Status:</span> <span className="text-primary-ondark">EVAL_QUEUED</span></div>
              </div>
              <button 
                onClick={() => navigate('/')}
                className="w-full bg-primary hover:bg-primary-hover active:scale-95 text-white py-2.5 rounded-lg text-xs font-medium transition-all"
              >
                Return to Home
              </button>
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
