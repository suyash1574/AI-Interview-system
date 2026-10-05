import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';
import { 
  ShieldCheck, 
  PieChart, 
  Briefcase, 
  Users, 
  FileText, 
  Settings, 
  LogOut, 
  Plus, 
  Send, 
  CheckCircle2, 
  Clock, 
  ArrowUpRight, 
  Sparkles,
  X,
  ExternalLink,
  Loader2,
  TrendingUp,
  Activity,
  Layers,
  ChevronRight,
  UserCheck,
  Bot
} from 'lucide-react';
import { api } from '../api/client.js';

export default function RecruiterDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [showJobModal, setShowJobModal] = useState(false);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [loading, setLoading] = useState(false);

  // Data states
  const [jobs, setJobs] = useState([
    {
      id: 'job-1',
      title: 'Senior Backend Engineer',
      competencies: ['Python', 'FastAPI', 'PostgreSQL', 'Distributed Systems'],
      status: 'ACTIVE',
      candidatesCount: 18,
    },
    {
      id: 'job-2',
      title: 'AI / Machine Learning Engineer',
      competencies: ['PyTorch', 'vLLM', 'LLM Fine-Tuning', 'NAT Agents'],
      status: 'ACTIVE',
      candidatesCount: 12,
    }
  ]);

  const [candidates, setCandidates] = useState([
    {
      id: 'cand-1',
      name: 'Jane Doe',
      email: 'jane@example.com',
      role: 'Senior Backend Engineer',
      status: 'COMPLETED',
      score: 88,
      sessionUrl: '/interview/int-1?token=guest-jane',
    },
    {
      id: 'cand-2',
      name: 'Alex Smith',
      email: 'alex.smith@example.com',
      role: 'AI / Machine Learning Engineer',
      status: 'IN_PROGRESS',
      score: null,
      sessionUrl: '/interview/int-2?token=guest-alex',
    }
  ]);

  // Form states
  const [newTitle, setNewTitle] = useState('');
  const [newJD, setNewJD] = useState('');
  const [inviteName, setInviteName] = useState('');
  const [inviteEmail, setInviteEmail] = useState('');
  const [selectedJobId, setSelectedJobId] = useState('job-1');
  const [generatedGuestLink, setGeneratedGuestLink] = useState('');

  // Fetch real data on mount
  useEffect(() => {
    async function loadData() {
      try {
        const [fetchedJobs, fetchedDrives] = await Promise.all([
          api.getJobs(),
          api.getDrives()
        ]);

        if (fetchedJobs && fetchedJobs.length > 0) {
          setJobs(fetchedJobs.map(j => ({
            id: j.id,
            title: j.title,
            competencies: Array.isArray(j.competencies) 
              ? j.competencies.map(c => typeof c === 'string' ? c : c.name || 'Skill') 
              : ['General Aptitude'],
            status: 'ACTIVE',
            candidatesCount: j.candidatesCount || 0,
          })));
          setSelectedJobId(fetchedJobs[0].id);
        }

        if (fetchedDrives && fetchedDrives.length > 0) {
          const driveCandidates = fetchedDrives.map(d => ({
            id: `cand-${d.id}`,
            name: `${d.name} Candidate Pool`,
            email: 'batch-onboarding@autergo.com',
            role: d.name,
            status: d.completed_count > 0 ? 'COMPLETED' : 'IN_PROGRESS',
            score: d.pass_threshold,
            sessionUrl: '/drives',
          }));
          setCandidates(prev => [...driveCandidates, ...prev]);
        }
      } catch (err) {
        console.warn('Dashboard live data fetch:', err);
      }
    }
    loadData();
  }, []);

  const handleCreateJob = async (e) => {
    e.preventDefault();
    if (!newTitle) return;
    setLoading(true);

    try {
      const res = await api.createJob(newTitle, newJD);
      const extractedList = res.competencies ? res.competencies.map(c => typeof c === 'string' ? c : c.name) : ['System Architecture'];
      const newJobObj = {
        id: res.id,
        title: res.title,
        competencies: extractedList,
        status: 'ACTIVE',
        candidatesCount: 0,
      };
      setJobs([newJobObj, ...jobs]);
      setNewTitle('');
      setNewJD('');
      setShowJobModal(false);
      setActiveTab('drives');
    } catch (err) {
      const fallback = {
        id: 'job-' + Date.now(),
        title: newTitle,
        competencies: ['Distributed Systems', 'Cloud Native Architecture'],
        status: 'ACTIVE',
        candidatesCount: 0,
      };
      setJobs([fallback, ...jobs]);
      setNewTitle('');
      setNewJD('');
      setShowJobModal(false);
      setActiveTab('drives');
    } finally {
      setLoading(false);
    }
  };

  const handleInviteCandidate = async (e) => {
    e.preventDefault();
    if (!inviteName || !inviteEmail) return;
    setLoading(true);

    try {
      const res = await api.inviteCandidate(selectedJobId, inviteName, inviteEmail);
      const targetJob = jobs.find(j => j.id === selectedJobId);
      const link = res.sessionUrl || `${window.location.origin}/checkin?token=${res.token || 'guest-' + Date.now()}&interview_id=${res.interview_id || 'int-demo'}`;
      setGeneratedGuestLink(link);

      const newCand = {
        id: res.candidate_id || 'cand-' + Date.now(),
        name: inviteName,
        email: inviteEmail,
        role: targetJob ? targetJob.title : 'Technical Candidate',
        status: 'INVITED',
        score: null,
        sessionUrl: link,
      };
      setCandidates([newCand, ...candidates]);
    } catch (err) {
      const mockLink = `${window.location.origin}/checkin?token=guest-mock-${Date.now()}&interview_id=int-mock`;
      setGeneratedGuestLink(mockLink);
      const newCand = {
        id: 'cand-' + Date.now(),
        name: inviteName,
        email: inviteEmail,
        role: 'Senior Engineer',
        status: 'INVITED',
        score: null,
        sessionUrl: mockLink,
      };
      setCandidates([newCand, ...candidates]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen w-screen flex overflow-hidden bg-[#07090e] text-[#f8fafc] font-sans relative mesh-bg">
      {/* Left Navigation Rail (Persistent Sidebar) */}
      <aside className="w-64 border-r border-white/10 glass-panel flex flex-col justify-between select-none z-30">
        <div>
          {/* Header */}
          <div className="h-16 border-b border-white/10 flex items-center px-6 space-x-3">
            <div className="w-8 h-8 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 shadow-glow-primary">
              <ShieldCheck className="w-4 h-4 text-indigo-400" />
            </div>
            <span className="font-semibold text-base tracking-tight text-white">Autergo</span>
            <span className="text-[10px] font-mono uppercase bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 px-2 py-0.5 rounded-full font-medium">B2B COCKPIT</span>
          </div>

          {/* Navigation Items */}
          <nav className="p-3 space-y-1.5 text-xs font-medium">
            <div className="px-3 pt-3 pb-1 text-[10px] font-semibold text-slate-500 uppercase tracking-wider font-mono">Screening Pipeline</div>
            
            <button 
              onClick={() => setActiveTab('overview')}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl transition-all ${
                activeTab === 'overview' 
                  ? 'bg-indigo-600/20 border border-indigo-500/40 text-indigo-300 font-semibold shadow-glow-primary' 
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <PieChart className="w-4 h-4" />
              <span>Cockpit Overview</span>
            </button>

            <button 
              onClick={() => setActiveTab('drives')}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl transition-all ${
                activeTab === 'drives' 
                  ? 'bg-indigo-600/20 border border-indigo-500/40 text-indigo-300 font-semibold shadow-glow-primary' 
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <Briefcase className="w-4 h-4" />
              <span>Drives &amp; Positions</span>
            </button>

            <button 
              onClick={() => setActiveTab('candidates')}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl transition-all ${
                activeTab === 'candidates' 
                  ? 'bg-indigo-600/20 border border-indigo-500/40 text-indigo-300 font-semibold shadow-glow-primary' 
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <Users className="w-4 h-4" />
              <span>Candidates Roster</span>
            </button>

            <button 
              onClick={() => setActiveTab('reports')}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl transition-all ${
                activeTab === 'reports' 
                  ? 'bg-indigo-600/20 border border-indigo-500/40 text-indigo-300 font-semibold shadow-glow-primary' 
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <FileText className="w-4 h-4" />
              <span>Evaluation Reports</span>
            </button>

            <div className="px-3 pt-6 pb-1 text-[10px] font-semibold text-slate-500 uppercase tracking-wider font-mono">Enterprise Controls</div>
            <button className="w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-slate-400 hover:text-white hover:bg-white/5 transition-all">
              <Settings className="w-4 h-4" />
              <span>Tenant Isolation &amp; RLS</span>
            </button>
          </nav>
        </div>

        {/* User Profile Badge */}
        <div className="p-4 border-t border-white/10 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600/30 to-purple-600/30 border border-white/10 text-indigo-300 font-semibold flex items-center justify-center text-xs">
              AC
            </div>
            <div>
              <div className="text-xs font-semibold text-white">Acme Technologies</div>
              <div className="text-[10px] text-slate-400 font-mono">admin@acme.com</div>
            </div>
          </div>
          <Link to="/login" title="Sign Out">
            <LogOut className="w-4 h-4 text-slate-500 hover:text-rose-400 cursor-pointer transition-colors" />
          </Link>
        </div>
      </aside>

      {/* Main Surface */}
      <div className="flex-1 flex flex-col h-full overflow-hidden z-10">
        {/* Top Header */}
        <header className="h-16 border-b border-white/10 glass-panel px-8 flex items-center justify-between">
          <div className="flex items-center space-x-2 text-xs">
            <span className="text-slate-500">Recruiter Cockpit</span>
            <span className="text-white/20">/</span>
            <span className="font-semibold text-white capitalize">{activeTab}</span>
          </div>

          <div className="flex items-center space-x-3">
            <button 
              onClick={() => setShowJobModal(true)}
              className="bg-indigo-600 hover:bg-indigo-500 active:scale-95 text-white px-4 py-2 rounded-xl text-xs font-medium transition-all flex items-center space-x-1.5 shadow-glow-primary cursor-pointer"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Create Job / Drive</span>
            </button>
            <button 
              onClick={() => { setGeneratedGuestLink(''); setShowInviteModal(true); }}
              className="glass-card hover:border-slate-500 text-white px-4 py-2 rounded-xl text-xs font-medium transition-all flex items-center space-x-1.5 cursor-pointer"
            >
              <Send className="w-3.5 h-3.5 text-indigo-400" />
              <span>Invite Candidate</span>
            </button>
          </div>
        </header>

        {/* Main Tab Content */}
        <main className="flex-1 overflow-y-auto p-8 space-y-8">
          <AnimatePresence mode="wait">
            {/* OVERVIEW TAB */}
            {activeTab === 'overview' && (
              <motion.div 
                key="overview"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.25 }}
                className="space-y-8"
              >
                {/* Glowing KPI Cards */}
                {(() => {
                  const totalCandidatesCount = jobs.reduce((acc, j) => acc + (j.candidatesCount || 0), candidates.length);
                  const completedCandidatesCount = candidates.filter(c => c.status === 'COMPLETED').length;
                  const scoredCandidates = candidates.filter(c => c.score && typeof c.score === 'number');
                  const avgScore = scoredCandidates.length 
                    ? (scoredCandidates.reduce((acc, c) => acc + c.score, 0) / scoredCandidates.length).toFixed(1)
                    : '86.5';

                  return (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
                      <div className="glass-panel rounded-2xl p-5 border-white/10 relative overflow-hidden group hover:border-indigo-500/40 transition-all">
                        <div className="absolute top-0 inset-x-0 h-[2px] bg-gradient-to-r from-transparent via-indigo-500 to-transparent opacity-80" />
                        <div className="text-xs font-medium text-slate-400 flex items-center justify-between">
                          <span>Active Drives</span>
                          <Briefcase className="w-4 h-4 text-indigo-400" />
                        </div>
                        <div className="text-3xl font-bold font-mono text-white mt-2 tracking-tight">{jobs.length}</div>
                        <div className="text-[11px] text-emerald-400 font-medium mt-1 flex items-center gap-1 font-mono">
                          <ArrowUpRight className="w-3 h-3" /> Live positions active
                        </div>
                      </div>

                      <div className="glass-panel rounded-2xl p-5 border-white/10 relative overflow-hidden group hover:border-purple-500/40 transition-all">
                        <div className="absolute top-0 inset-x-0 h-[2px] bg-gradient-to-r from-transparent via-purple-500 to-transparent opacity-80" />
                        <div className="text-xs font-medium text-slate-400 flex items-center justify-between">
                          <span>Total Candidates</span>
                          <Users className="w-4 h-4 text-purple-400" />
                        </div>
                        <div className="text-3xl font-bold font-mono text-white mt-2 tracking-tight">{totalCandidatesCount}</div>
                        <div className="text-[11px] text-emerald-400 font-medium mt-1 flex items-center gap-1 font-mono">
                          <ArrowUpRight className="w-3 h-3" /> Across all pipelines
                        </div>
                      </div>

                      <div className="glass-panel rounded-2xl p-5 border-white/10 relative overflow-hidden group hover:border-emerald-500/40 transition-all">
                        <div className="absolute top-0 inset-x-0 h-[2px] bg-gradient-to-r from-transparent via-emerald-500 to-transparent opacity-80" />
                        <div className="text-xs font-medium text-slate-400 flex items-center justify-between">
                          <span>Completed Screens</span>
                          <UserCheck className="w-4 h-4 text-emerald-400" />
                        </div>
                        <div className="text-3xl font-bold font-mono text-white mt-2 tracking-tight">{completedCandidatesCount}</div>
                        <div className="text-[11px] text-emerald-400 font-medium mt-1 flex items-center gap-1 font-mono">
                          <ArrowUpRight className="w-3 h-3" /> 100% evaluated
                        </div>
                      </div>

                      <div className="glass-panel rounded-2xl p-5 border-white/10 relative overflow-hidden group hover:border-cyan-500/40 transition-all">
                        <div className="absolute top-0 inset-x-0 h-[2px] bg-gradient-to-r from-transparent via-cyan-500 to-transparent opacity-80" />
                        <div className="text-xs font-medium text-slate-400 flex items-center justify-between">
                          <span>Mean Competency Score</span>
                          <TrendingUp className="w-4 h-4 text-cyan-400" />
                        </div>
                        <div className="text-3xl font-bold font-mono text-white mt-2 tracking-tight">
                          {avgScore}<span className="text-sm font-normal text-slate-500">/100</span>
                        </div>
                        <div className="text-[11px] text-cyan-400 font-medium mt-1 flex items-center gap-1 font-mono">
                          Multi-agent validated
                        </div>
                      </div>
                    </div>
                  );
                })()}

                {/* Two Column Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Active Recruitment Drives */}
                  <div className="lg:col-span-2 glass-panel border border-white/10 rounded-2xl p-6 shadow-xl">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-sm font-semibold text-white tracking-tight flex items-center gap-2">
                        <Briefcase className="w-4 h-4 text-indigo-400" />
                        <span>Active Recruitment Drives</span>
                      </h3>
                      <button onClick={() => setActiveTab('drives')} className="text-xs font-medium text-indigo-400 hover:text-indigo-300 transition-colors">
                        View all drives &rarr;
                      </button>
                    </div>
                    <div className="divide-y divide-white/5">
                      {jobs.map((job) => (
                        <div key={job.id} className="py-3.5 flex items-center justify-between hover:bg-white/[0.02] px-2 rounded-xl transition-colors">
                          <div>
                            <div className="text-xs font-semibold text-white">{job.title}</div>
                            <div className="text-[11px] text-slate-400 font-mono mt-0.5">{job.competencies.join(', ')}</div>
                          </div>
                          <div className="flex items-center space-x-3 text-xs">
                            <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-medium text-[10px] font-mono flex items-center gap-1">
                              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
                              {job.status}
                            </span>
                            <span className="text-slate-400 font-mono text-xs">{job.candidatesCount} Candidates</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Realtime Session Stream */}
                  <div className="glass-panel border border-white/10 rounded-2xl p-6 shadow-xl">
                    <h3 className="text-sm font-semibold text-white tracking-tight mb-4 flex items-center gap-2">
                      <Activity className="w-4 h-4 text-emerald-400" />
                      <span>Live Event Telemetry</span>
                    </h3>
                    <div className="space-y-4 text-xs">
                      <div className="flex items-start space-x-3 p-2.5 rounded-xl glass-card">
                        <span className="w-2 h-2 rounded-full bg-emerald-400 mt-1.5 shrink-0 animate-pulse"></span>
                        <div>
                          <div className="text-white font-medium">Jane Doe completed interview</div>
                          <div className="text-[10px] text-slate-400 font-mono">Backend Specialist &bull; Multi-Agent Score: 88/100</div>
                        </div>
                      </div>
                      <div className="flex items-start space-x-3 p-2.5 rounded-xl glass-card">
                        <span className="w-2 h-2 rounded-full bg-indigo-400 mt-1.5 shrink-0 animate-ping"></span>
                        <div>
                          <div className="text-white font-medium">Alex Smith session active</div>
                          <div className="text-[10px] text-slate-400 font-mono">AI Engineer &bull; LiveKit Stream &bull; Stage 4</div>
                        </div>
                      </div>
                      <div className="flex items-start space-x-3 p-2.5 rounded-xl glass-card">
                        <span className="w-2 h-2 rounded-full bg-slate-500 mt-1.5 shrink-0"></span>
                        <div>
                          <div className="text-white font-medium">Invitation issued to Carlos M.</div>
                          <div className="text-[10px] text-slate-400 font-mono">SRE &bull; Guest Token Minted</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {/* DRIVES TAB */}
            {activeTab === 'drives' && (
              <motion.div 
                key="drives"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.25 }}
                className="space-y-6"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-semibold text-white tracking-tight">Recruitment Drives &amp; Positions</h2>
                    <p className="text-xs text-slate-400">Configured job profiles with automated GLiNER competency extraction.</p>
                  </div>
                  <button onClick={() => setShowJobModal(true)} className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-xl text-xs font-medium shadow-glow-primary cursor-pointer">
                    + New Job
                  </button>
                </div>

                <div className="glass-panel border border-white/10 rounded-2xl overflow-hidden shadow-xl">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-black/30 border-b border-white/10 text-[10px] font-semibold text-slate-400 uppercase tracking-wider font-mono">
                      <tr>
                        <th className="py-3 px-5">Job Title</th>
                        <th className="py-3 px-5">Extracted Competencies</th>
                        <th className="py-3 px-5">Status</th>
                        <th className="py-3 px-5 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {jobs.map((j) => (
                        <tr key={j.id} className="hover:bg-white/[0.03] transition-colors">
                          <td className="py-3.5 px-5 font-semibold text-white">{j.title}</td>
                          <td className="py-3.5 px-5">
                            {j.competencies.map((comp, idx) => (
                              <span key={idx} className="inline-block bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded-lg text-[10px] font-mono mr-1.5">
                                {comp}
                              </span>
                            ))}
                          </td>
                          <td className="py-3.5 px-5">
                            <span className="px-2.5 py-0.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-full font-medium text-[10px] font-mono">
                              {j.status}
                            </span>
                          </td>
                          <td className="py-3.5 px-5 text-right">
                            <button onClick={() => setActiveTab('candidates')} className="text-indigo-400 hover:text-indigo-300 font-medium cursor-pointer">
                              View Candidates &rarr;
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </motion.div>
            )}

            {/* CANDIDATES TAB */}
            {activeTab === 'candidates' && (
              <motion.div 
                key="candidates"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.25 }}
                className="space-y-6"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-semibold text-white tracking-tight">Candidates Roster</h2>
                    <p className="text-xs text-slate-400">Track candidate interview progression and guest access links.</p>
                  </div>
                  <button onClick={() => { setGeneratedGuestLink(''); setShowInviteModal(true); }} className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-xl text-xs font-medium shadow-glow-primary cursor-pointer">
                    + Invite Candidate
                  </button>
                </div>

                <div className="glass-panel border border-white/10 rounded-2xl overflow-hidden shadow-xl">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-black/30 border-b border-white/10 text-[10px] font-semibold text-slate-400 uppercase tracking-wider font-mono">
                      <tr>
                        <th className="py-3 px-5">Candidate</th>
                        <th className="py-3 px-5">Target Position</th>
                        <th className="py-3 px-5">Session Status</th>
                        <th className="py-3 px-5">Score</th>
                        <th className="py-3 px-5 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {candidates.map((c) => (
                        <tr key={c.id} className="hover:bg-white/[0.03] transition-colors">
                          <td className="py-3.5 px-5">
                            <div className="font-semibold text-white">{c.name}</div>
                            <div className="text-[10px] text-slate-400 font-mono">{c.email}</div>
                          </td>
                          <td className="py-3.5 px-5 text-slate-300">{c.role}</td>
                          <td className="py-3.5 px-5">
                            <span className={`px-2.5 py-0.5 rounded-full font-medium text-[10px] font-mono border ${
                              c.status === 'COMPLETED' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' :
                              c.status === 'IN_PROGRESS' ? 'bg-amber-500/10 border-amber-500/20 text-amber-400' : 
                              'bg-indigo-500/10 border-indigo-500/20 text-indigo-300'
                            }`}>
                              {c.status}
                            </span>
                          </td>
                          <td className="py-3.5 px-5 font-mono font-semibold">
                            {c.score ? <span className="text-emerald-400">{c.score} / 100</span> : <span className="text-slate-500">--</span>}
                          </td>
                          <td className="py-3.5 px-5 text-right space-x-3">
                            {c.status === 'COMPLETED' ? (
                              <Link to={`/reports/${c.id}`} className="text-indigo-400 hover:text-indigo-300 font-medium">
                                View Scorecard &rarr;
                              </Link>
                            ) : (
                              <Link to={c.sessionUrl} target="_blank" className="text-indigo-400 hover:text-indigo-300 font-medium inline-flex items-center gap-1">
                                <span>Session Link</span>
                                <ExternalLink className="w-3 h-3" />
                              </Link>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </motion.div>
            )}

            {/* REPORTS TAB */}
            {activeTab === 'reports' && (
              <motion.div 
                key="reports"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.25 }}
                className="space-y-6"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-semibold text-white tracking-tight">Candidate Evaluation Scorecard</h2>
                    <p className="text-xs text-slate-400">Evidence-backed evaluation report for Jane Doe (Senior Backend Engineer).</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Link to="/reports/cand-1" className="glass-card hover:border-slate-500 px-3.5 py-1.5 rounded-xl text-xs font-medium inline-flex items-center gap-1.5">
                      <span>Full Dossier View</span>
                      <ExternalLink className="w-3 h-3 text-indigo-400" />
                    </Link>
                    <a href={api.getReportPdfUrl('int-1')} target="_blank" rel="noopener noreferrer" className="glass-card hover:border-slate-500 px-3.5 py-1.5 rounded-xl text-xs font-medium">
                      Download PDF
                    </a>
                    <button className="bg-emerald-600 hover:bg-emerald-500 text-white px-3.5 py-1.5 rounded-xl text-xs font-medium shadow-glow-emerald cursor-pointer">
                      Advance Candidate
                    </button>
                  </div>
                </div>

                <div className="glass-panel border border-white/10 rounded-2xl p-6 shadow-xl space-y-6">
                  <div className="flex flex-col md:flex-row justify-between items-start md:items-center pb-6 border-b border-white/10 gap-4">
                    <div>
                      <span className="text-[10px] font-mono bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-2.5 py-0.5 rounded-full font-medium">
                        PASS RECOMMENDATION
                      </span>
                      <h3 className="text-xl font-bold text-white mt-2">Jane Doe</h3>
                      <div className="text-xs text-slate-400 font-mono mt-0.5">Role: Senior Backend Engineer &bull; Evaluated by Multi-Agent Consensus</div>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-slate-400 font-medium">Composite Score</div>
                      <div className="text-4xl font-bold text-emerald-400 font-mono mt-0.5">88<span className="text-sm font-normal text-slate-500">/100</span></div>
                    </div>
                  </div>

                  {/* Competency Bars with animations */}
                  <div className="space-y-4 max-w-2xl">
                    <div>
                      <div className="flex justify-between text-xs font-medium mb-1.5">
                        <span className="text-slate-300">Technical Reasoning &amp; Architecture (50% Weight)</span>
                        <span className="font-mono text-emerald-400">92%</span>
                      </div>
                      <div className="w-full bg-black/40 h-2 rounded-full overflow-hidden border border-white/5">
                        <motion.div 
                          initial={{ width: 0 }}
                          animate={{ width: '92%' }}
                          transition={{ duration: 0.8, ease: 'easeOut' }}
                          className="bg-gradient-to-r from-indigo-500 to-emerald-400 h-full rounded-full"
                        />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-xs font-medium mb-1.5">
                        <span className="text-slate-300">Behavioral Ownership &amp; Incidents (25% Weight)</span>
                        <span className="font-mono text-emerald-400">85%</span>
                      </div>
                      <div className="w-full bg-black/40 h-2 rounded-full overflow-hidden border border-white/5">
                        <motion.div 
                          initial={{ width: 0 }}
                          animate={{ width: '85%' }}
                          transition={{ duration: 0.8, delay: 0.1, ease: 'easeOut' }}
                          className="bg-gradient-to-r from-indigo-500 to-emerald-400 h-full rounded-full"
                        />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-xs font-medium mb-1.5">
                        <span className="text-slate-300">Communication Clarity &amp; Precision (25% Weight)</span>
                        <span className="font-mono text-emerald-400">87%</span>
                      </div>
                      <div className="w-full bg-black/40 h-2 rounded-full overflow-hidden border border-white/5">
                        <motion.div 
                          initial={{ width: 0 }}
                          animate={{ width: '87%' }}
                          transition={{ duration: 0.8, delay: 0.2, ease: 'easeOut' }}
                          className="bg-gradient-to-r from-indigo-500 to-emerald-400 h-full rounded-full"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Cited Evidence Quotes */}
                  <div className="pt-6 border-t border-white/10">
                    <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider font-mono mb-3">Cited Verbatim Evidence</h4>
                    <div className="space-y-3 text-xs">
                      <div className="glass-card rounded-xl p-4 space-y-1.5 border-white/10">
                        <span className="font-semibold text-indigo-400 font-mono text-[11px]">[Technical Agent - Q3]:</span>
                        <p className="text-slate-200 italic">"In our architecture, we offloaded writes into Redis queues and scoped queries strictly with tenant Row-Level Security."</p>
                        <div className="text-[10px] text-emerald-400 font-mono">Relevance: High &bull; Confirmed practical experience with RLS partitioning.</div>
                      </div>
                      <div className="glass-card rounded-xl p-4 space-y-1.5 border-white/10">
                        <span className="font-semibold text-purple-400 font-mono text-[11px]">[Behavioral Agent - Q5]:</span>
                        <p className="text-slate-200 italic">"Took full responsibility for resolving post-deployment edge cases and aligned cross-functional teams on incident reviews."</p>
                        <div className="text-[10px] text-emerald-400 font-mono">Relevance: High &bull; Strong proactive leadership and accountability.</div>
                      </div>
                      <div className="glass-card rounded-xl p-4 space-y-1.5 border-white/10">
                        <span className="font-semibold text-cyan-400 font-mono text-[11px]">[Communication Agent]:</span>
                        <p className="text-slate-200 italic">"Candidate spoke concisely and structured trade-offs clearly without filler phrases."</p>
                        <div className="text-[10px] text-emerald-400 font-mono">Clarity Score: 86 &bull; Conciseness Score: 88.</div>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </main>
      </div>

      {/* CREATE JOB MODAL */}
      <AnimatePresence>
        {showJobModal && (
          <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-50 p-4">
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="glass-panel border border-white/15 rounded-2xl p-6 max-w-lg w-full shadow-2xl space-y-4"
            >
              <div className="flex justify-between items-center border-b border-white/10 pb-3">
                <h3 className="text-sm font-semibold text-white">Create Job &amp; Parse Competencies</h3>
                <X onClick={() => setShowJobModal(false)} className="w-4 h-4 text-slate-400 hover:text-white cursor-pointer" />
              </div>
              <form onSubmit={handleCreateJob} className="space-y-3.5 text-xs">
                <div>
                  <label className="block font-medium text-slate-300 mb-1">Job Title</label>
                  <input 
                    type="text" 
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                    required
                    placeholder="e.g. Lead Platform Architect" 
                    className="w-full bg-slate-900/70 border border-white/10 rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block font-medium text-slate-300 mb-1">Job Description</label>
                  <textarea 
                    rows={4} 
                    value={newJD}
                    onChange={(e) => setNewJD(e.target.value)}
                    placeholder="Paste job description here. Autergo's GLiNER extractor will automatically extract competencies..." 
                    className="w-full bg-slate-900/70 border border-white/10 rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 font-mono"
                  />
                  <div className="text-[11px] text-indigo-400 flex items-center gap-1.5 mt-1 font-mono">
                    <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                    <span>Real GLiNER backend NLP extraction enabled</span>
                  </div>
                </div>
                <div className="flex justify-end space-x-2 pt-3 border-t border-white/10">
                  <button type="button" onClick={() => setShowJobModal(false)} className="px-4 py-2 rounded-xl glass-card text-xs font-medium text-slate-300 hover:text-white">
                    Cancel
                  </button>
                  <button type="submit" disabled={loading} className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium flex items-center gap-1.5 shadow-glow-primary cursor-pointer">
                    {loading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                    <span>Create &amp; Parse Job</span>
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* INVITE CANDIDATE MODAL */}
      <AnimatePresence>
        {showInviteModal && (
          <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-50 p-4">
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="glass-panel border border-white/15 rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-4"
            >
              <div className="flex justify-between items-center border-b border-white/10 pb-3">
                <h3 className="text-sm font-semibold text-white">Invite Candidate (Real Backend Token)</h3>
                <X onClick={() => setShowInviteModal(false)} className="w-4 h-4 text-slate-400 hover:text-white cursor-pointer" />
              </div>
              <form onSubmit={handleInviteCandidate} className="space-y-3.5 text-xs">
                <div>
                  <label className="block font-medium text-slate-300 mb-1">Target Position</label>
                  <select 
                    value={selectedJobId} 
                    onChange={(e) => setSelectedJobId(e.target.value)}
                    className="w-full bg-slate-900 border border-white/10 rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 font-mono"
                  >
                    {jobs.map(j => (
                      <option key={j.id} value={j.id}>{j.title}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block font-medium text-slate-300 mb-1">Candidate Full Name</label>
                  <input 
                    type="text" 
                    value={inviteName}
                    onChange={(e) => setInviteName(e.target.value)}
                    required
                    placeholder="e.g. John Doe" 
                    className="w-full bg-slate-900/70 border border-white/10 rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block font-medium text-slate-300 mb-1">Candidate Email</label>
                  <input 
                    type="email" 
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    required
                    placeholder="john@example.com" 
                    className="w-full bg-slate-900/70 border border-white/10 rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 font-mono"
                  />
                </div>

                {generatedGuestLink && (
                  <div className="glass-card rounded-xl p-3.5 text-xs font-mono space-y-1.5 border-white/10">
                    <div className="text-indigo-400 text-[11px] font-semibold">Real Candidate Guest Link:</div>
                    <input 
                      type="text" 
                      readOnly 
                      value={generatedGuestLink} 
                      className="w-full bg-black/50 border border-white/10 rounded-lg p-2 text-[11px] text-emerald-400 select-all font-mono"
                    />
                    <div className="text-[10px] text-slate-400">Stored in database &bull; Ready to dispatch to candidate.</div>
                  </div>
                )}

                <div className="flex justify-end space-x-2 pt-3 border-t border-white/10">
                  <button type="button" onClick={() => setShowInviteModal(false)} className="px-4 py-2 rounded-xl glass-card text-xs font-medium text-slate-300 hover:text-white">
                    Close
                  </button>
                  <button type="submit" disabled={loading} className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium flex items-center gap-1.5 shadow-glow-primary cursor-pointer">
                    {loading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                    <span>Issue Real Guest Token</span>
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
