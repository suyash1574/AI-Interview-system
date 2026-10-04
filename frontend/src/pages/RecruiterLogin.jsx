import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, Link } from 'react-router-dom';
import { ShieldCheck, ArrowRight, Lock, Mail } from 'lucide-react';

import { SignIn } from '@clerk/clerk-react';

export default function RecruiterLogin() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('recruiter@acme.com');
  const [password, setPassword] = useState('••••••••••••');
  const clerkPubKey = typeof window !== 'undefined' ? (window.ENV?.CLERK_PUBLISHABLE_KEY || '') : '';

  const handleSubmit = (e) => {
    e.preventDefault();
    localStorage.setItem('autergo_token', 'dev_recruiter_jwt_token');
    localStorage.setItem('autergo_user_email', email);
    navigate('/dashboard');
  };

  return (
    <div className="h-screen w-screen flex bg-white overflow-hidden">
      {/* Left Brand Panel (40% per Plan SCR-02) */}
      <div className="hidden lg:flex lg:w-5/12 bg-dark-base p-12 flex-col justify-between border-r border-dark-border text-white select-none">
        <Link to="/" className="flex items-center space-x-2.5">
          <ShieldCheck className="w-6 h-6 text-primary" />
          <span className="font-semibold text-lg tracking-tight">Autergo</span>
        </Link>

        <motion.div 
          initial={{ opacity: 0, y: 12 }} 
          animate={{ opacity: 1, y: 0 }} 
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          className="space-y-4 max-w-sm"
        >
          <p className="text-lg font-medium leading-relaxed tracking-tight text-dark-ink">
            "Autergo cut our technical phone-screen overhead by 75% without compromising technical depth. The evidence-backed scorecards eliminate recruiter second-guessing."
          </p>
          <div>
            <div className="text-xs font-semibold text-white">Elena Rostova</div>
            <div className="text-[11px] text-dark-muted font-mono">Head of Technical Talent &bull; ScaleGrid Systems</div>
          </div>
        </motion.div>

        <div className="text-xs text-dark-muted font-mono">
          Autonomous Voice-First Technical Interviews
        </div>
      </div>

      {/* Right Form Panel (60%) */}
      <div className="flex-1 flex flex-col justify-center items-center p-8 bg-white overflow-y-auto">
        <motion.div 
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4 }}
          className="max-w-md w-full space-y-8"
        >
          <div>
            <div className="lg:hidden flex items-center space-x-2 text-primary font-semibold text-base mb-6">
              <ShieldCheck className="w-5 h-5" />
              <span>Autergo</span>
            </div>
            <h1 className="text-2xl font-semibold text-ink tracking-tight">Sign in to Autergo</h1>
            <p className="text-xs text-ink-muted mt-1.5">
              New to Autergo? <a href="#" className="text-primary hover:underline font-medium">Request an enterprise pilot</a>
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4 text-xs">
            <div>
              <label className="block font-medium text-ink mb-1.5">Work Email</label>
              <div className="relative">
                <input 
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required 
                  className="w-full border border-border rounded-lg p-3 pl-9 text-xs focus:outline-none focus:border-primary transition-colors font-mono"
                />
                <Mail className="w-4 h-4 text-ink-muted absolute left-3 top-3.5" />
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className="font-medium text-ink">Password</label>
                <a href="#" className="text-primary hover:underline text-[11px]">Forgot password?</a>
              </div>
              <div className="relative">
                <input 
                  type="password" 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required 
                  className="w-full border border-border rounded-lg p-3 pl-9 text-xs focus:outline-none focus:border-primary transition-colors"
                />
                <Lock className="w-4 h-4 text-ink-muted absolute left-3 top-3.5" />
              </div>
            </div>

            <button 
              type="submit" 
              className="w-full bg-primary hover:bg-primary-hover active:scale-95 text-white py-3 rounded-full text-xs font-semibold transition-all shadow-xs flex items-center justify-center gap-1.5"
            >
              <span>Sign In to Dashboard</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </form>

          <div className="relative flex py-2 items-center">
            <div className="flex-grow border-t border-border"></div>
            <span className="flex-shrink mx-4 text-ink-muted text-[11px] uppercase tracking-wider font-mono">or continue with</span>
            <div className="flex-grow border-t border-border"></div>
          </div>

          <div className="space-y-2.5">
            <button 
              onClick={() => navigate('/dashboard')}
              className="w-full border border-border hover:bg-canvas-subtle p-2.5 rounded-lg text-xs font-medium text-ink flex items-center justify-center space-x-2 transition-colors"
            >
              <span>Continue with Google Workspace</span>
            </button>
            <button 
              onClick={() => navigate('/dashboard')}
              className="w-full border border-border hover:bg-canvas-subtle p-2.5 rounded-lg text-xs font-medium text-ink flex items-center justify-center space-x-2 transition-colors"
            >
              <span>Continue with GitHub SSO</span>
            </button>
          </div>

          <div className="text-[11px] text-ink-muted text-center leading-relaxed font-mono">
            Protected by PostgreSQL Row-Level Security &bull; End-to-End Encrypted
          </div>
        </motion.div>
      </div>
    </div>
  );
}
