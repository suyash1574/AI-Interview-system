import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, Link } from 'react-router-dom';
import { ShieldCheck, ArrowRight, Lock, Mail, Sparkles, CheckCircle2 } from 'lucide-react';
import { SignIn } from '@clerk/clerk-react';

export default function RecruiterLogin() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('recruiter@acme.com');
  const [password, setPassword] = useState('••••••••••••');
  const clerkPubKey = import.meta.env?.VITE_CLERK_PUBLISHABLE_KEY || (typeof window !== 'undefined' ? window.ENV?.CLERK_PUBLISHABLE_KEY : '');
  const hasClerk = Boolean(clerkPubKey && !clerkPubKey.includes('placeholder'));
  const [useClerk, setUseClerk] = useState(hasClerk);

  const handleSubmit = (e) => {
    e.preventDefault();
    localStorage.setItem('autergo_token', 'dev_recruiter_jwt_token');
    localStorage.setItem('autergo_user_email', email);
    navigate('/dashboard');
  };

  return (
    <div className="h-screen w-screen flex bg-[#07090e] text-[#f8fafc] overflow-hidden font-sans relative mesh-bg">
      {/* Ambient background glow */}
      <div className="absolute top-1/3 left-1/4 w-[500px] h-[300px] bg-indigo-600/15 rounded-full blur-[140px] pointer-events-none -z-10" />

      {/* Left Brand Panel */}
      <div className="hidden lg:flex lg:w-5/12 glass-panel p-12 flex-col justify-between border-r border-white/10 select-none z-10">
        <Link to="/" className="flex items-center space-x-2.5 group">
          <div className="w-9 h-9 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 group-hover:scale-105 transition-transform shadow-glow-primary">
            <ShieldCheck className="w-5 h-5 text-indigo-400" />
          </div>
          <span className="font-bold text-lg tracking-tight text-white">Autergo</span>
        </Link>

        <motion.div 
          initial={{ opacity: 0, y: 12 }} 
          animate={{ opacity: 1, y: 0 }} 
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          className="space-y-4 max-w-sm"
        >
          <div className="w-8 h-8 rounded-full bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
            <Sparkles className="w-4 h-4" />
          </div>
          <p className="text-lg font-medium leading-relaxed tracking-tight text-slate-200">
            "Autergo cut our technical phone-screen overhead by 75% without compromising technical depth. The evidence-backed scorecards eliminate recruiter second-guessing."
          </p>
          <div>
            <div className="text-xs font-semibold text-white">Elena Rostova</div>
            <div className="text-[10px] text-slate-400 font-mono">Head of Technical Talent &bull; ScaleGrid Systems</div>
          </div>
        </motion.div>

        <div className="text-xs text-slate-500 font-mono flex items-center gap-2">
          <Lock className="w-3.5 h-3.5 text-indigo-400" />
          <span>PostgreSQL Row-Level Security Protected</span>
        </div>
      </div>

      {/* Right Form Panel */}
      <div className="flex-1 flex flex-col justify-center items-center p-8 overflow-y-auto z-10">
        <motion.div 
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4 }}
          className="max-w-md w-full space-y-6 glass-panel border border-white/10 p-8 rounded-3xl shadow-2xl relative overflow-hidden"
        >
          <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-indigo-500 to-purple-500" />

          <div>
            <div className="lg:hidden flex items-center space-x-2 text-indigo-400 font-semibold text-base mb-6">
              <ShieldCheck className="w-5 h-5" />
              <span>Autergo</span>
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">Sign in to Cockpit</h1>
            <p className="text-xs text-slate-400 mt-1.5">
              Access your multi-agent screening pipelines and candidate scorecards.
            </p>
          </div>

          {useClerk && hasClerk ? (
            <div className="space-y-4">
              <div className="flex justify-center">
                <SignIn routing="hash" redirectUrl="/dashboard" afterSignInUrl="/dashboard" />
              </div>
              <div className="text-center">
                <button 
                  onClick={() => setUseClerk(false)}
                  className="text-xs text-indigo-400 hover:underline font-medium cursor-pointer"
                >
                  Switch to Work Email / Demo Sign In
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <form onSubmit={handleSubmit} className="space-y-4 text-xs">
                <div>
                  <label className="block font-medium text-slate-300 mb-1.5">Work Email</label>
                  <div className="relative">
                    <input 
                      type="email" 
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required 
                      className="w-full bg-slate-900/70 border border-white/10 rounded-xl p-3 pl-9 text-xs text-white focus:outline-none focus:border-indigo-500 font-mono"
                    />
                    <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-3.5" />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between items-center mb-1.5">
                    <label className="font-medium text-slate-300">Password</label>
                    <a href="#" className="text-indigo-400 hover:underline text-[11px]">Forgot password?</a>
                  </div>
                  <div className="relative">
                    <input 
                      type="password" 
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required 
                      className="w-full bg-slate-900/70 border border-white/10 rounded-xl p-3 pl-9 text-xs text-white focus:outline-none focus:border-indigo-500"
                    />
                    <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-3.5" />
                  </div>
                </div>

                <button 
                  type="submit" 
                  className="w-full bg-indigo-600 hover:bg-indigo-500 active:scale-95 text-white py-3 rounded-xl text-xs font-semibold transition-all shadow-glow-primary flex items-center justify-center gap-1.5 cursor-pointer"
                >
                  <span>Sign In to Cockpit</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </form>

              <div className="relative flex py-2 items-center">
                <div className="flex-grow border-t border-white/10"></div>
                <span className="flex-shrink mx-4 text-slate-500 text-[10px] uppercase tracking-wider font-mono">or demo access</span>
                <div className="flex-grow border-t border-white/10"></div>
              </div>

              <div className="space-y-2">
                <button 
                  onClick={() => navigate('/dashboard')}
                  className="w-full glass-card hover:border-slate-500 p-2.5 rounded-xl text-xs font-medium text-slate-300 hover:text-white flex items-center justify-center space-x-2 transition-all cursor-pointer"
                >
                  <span>Continue with Demo Credentials</span>
                </button>
              </div>

              {hasClerk && (
                <div className="text-center pt-2">
                  <button 
                    onClick={() => setUseClerk(true)}
                    className="text-xs text-indigo-400 hover:underline font-medium cursor-pointer"
                  >
                    Switch back to Clerk SSO
                  </button>
                </div>
              )}
            </div>
          )}

          <div className="text-[10px] text-slate-500 text-center leading-relaxed font-mono">
            Protected by PostgreSQL Row-Level Security &bull; TLS Encrypted
          </div>
        </motion.div>
      </div>
    </div>
  );
}
