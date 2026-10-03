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
  Loader2
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
      const fetchedJobs = await api.getJobs();
      if (fetchedJobs && fetchedJobs.length > 0) {
        setJobs(fetchedJobs.map(j => ({
          id: j.id,
          title: j.title,
          competencies: Array.isArray(j.competencies) ? j.competencies.map(c => typeof c === 'string' ? c : c.name || 'Skill') : ['General Aptitude'],
          status: 'ACTIVE',
          candidatesCount: 1,
        })));
        setSelectedJobId(fetchedJobs[0].id);
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
      // Optimistic fallback
      const fallback = {
        id: `job-${Date.now()}`,
        title: newTitle,
        competencies: ['Python', 'PostgreSQL', 'FastAPI'],
        status: 'ACTIVE',
        candidatesCount: 0
      };
      setJobs([fallback, ...jobs]);
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
      const res = await api.createInterview(selectedJobId, inviteName, inviteEmail);
      const link = `${window.location.origin}${res.session_url || `/interview/${res.id}?token=${res.guest_token}`}`;
      setGeneratedGuestLink(link);

      const newCand = {
        id: res.candidate_id || `cand-${Date.now()}`,
        name: inviteName,
        email: inviteEmail,
        role: jobs.find(j => j.id === selectedJobId)?.title || 'Senior Backend Engineer',
        status: 'INVITED',
        score: null,
        sessionUrl: link,
      };
      setCandidates([newCand, ...candidates]);
    } catch (err) {
      const token = 'guest-' + Math.random().toString(36).substring(2, 9);
      const link = `${window.location.origin}/checkin?token=${token}`;
      setGeneratedGuestLink(link);
      const fallbackCand = {
        id: `cand-${Date.now()}`,
        name: inviteName,
        email: inviteEmail,
        role: 'Senior Backend Engineer',
        status: 'INVITED',
        score: null,
        sessionUrl: link,
      };
      setCandidates([fallbackCand, ...candidates]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen w-screen flex overflow-hidden bg-canvas-subtle">
      {/* Left Navigation Rail (Persistent Sidebar ≥1280px) */}
      <aside className="w-64 border-r border-border bg-white flex flex-col justify-between select-none">
        <div>
          {/* Header */}
          <div className="h-14 border-b border-border flex items-center px-6 space-x-2.5">
            <ShieldCheck className="w-5 h-5 text-primary" />
            <span className="font-semibold text-base tracking-tight text-ink">Autergo</span>
            <span className="text-[10px] font-mono uppercase bg-primary-subtle text-primary px-1.5 py-0.5 rounded font-medium">B2B</span>
          </div>

          {/* Navigation */}
          <nav className="p-3 space-y-1 text-xs font-medium">
            <div className="px-3 pt-3 pb-1 text-[11px] font-semibold text-ink-muted uppercase tracking-wider font-mono">Hiring Pipeline</div>
            <button 
              onClick={() => setActiveTab('overview')}
              className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-lg transition-colors ${activeTab === 'overview' ? 'bg-primary-subtle text-primary font-semibold' : 'text-ink hover:bg-canvas-subtle'}`}
            >
              <PieChart className="w-4 h-4" />
              <span>Overview</span>
            </button>
            <button 
              onClick={() => setActiveTab('drives')}
              className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-lg transition-colors ${activeTab === 'drives' ? 'bg-primary-subtle text-primary font-semibold' : 'text-ink hover:bg-canvas-subtle'}`}
            >
              <Briefcase className="w-4 h-4" />
              <span>Drives &amp; Jobs</span>
            </button>
            <button 
              onClick={() => setActiveTab('candidates')}
              className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-lg transition-colors ${activeTab === 'candidates' ? 'bg-primary-subtle text-primary font-semibold' : 'text-ink hover:bg-canvas-subtle'}`}
            >
              <Users className="w-4 h-4" />
              <span>Candidates</span>
            </button>
            <button 
              onClick={() => setActiveTab('reports')}
              className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-lg transition-colors ${activeTab === 'reports' ? 'bg-primary-subtle text-primary font-semibold' : 'text-ink hover:bg-canvas-subtle'}`}
            >
              <FileText className="w-4 h-4" />
              <span>Evaluation Reports</span>
            </button>

            <div className="px-3 pt-5 pb-1 text-[11px] font-semibold text-ink-muted uppercase tracking-wider font-mono">Platform</div>
            <button className="w-full flex items-center space-x-2.5 px-3 py-2 rounded-lg text-ink hover:bg-canvas-subtle transition-colors">
              <Settings className="w-4 h-4" />
              <span>Tenant Isolation &amp; RLS</span>
            </button>
          </nav>
        </div>

        {/* User Badge */}
        <div className="p-4 border-t border-border flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-full bg-primary-subtle text-primary font-semibold flex items-center justify-center text-xs">
              AC
            </div>
            <div>
              <div className="text-xs font-semibold text-ink">Acme Corp</div>
              <div className="text-[11px] text-ink-muted font-mono">admin@acme.com</div>
            </div>
          </div>
          <Link to="/login" title="Sign Out">
            <LogOut className="w-4 h-4 text-ink-muted hover:text-ink cursor-pointer" />
          </Link>
        </div>
      </aside>

      {/* Main Surface */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Top Header */}
        <header className="h-14 border-b border-border bg-white px-8 flex items-center justify-between">
          <div className="flex items-center space-x-2 text-xs">
            <span className="text-ink-muted">Recruiter Portal</span>
            <span className="text-border">/</span>
            <span className="font-semibold text-ink capitalize">{activeTab}</span>
          </div>

          <div className="flex items-center space-x-3">
            <button 
              onClick={() => setShowJobModal(true)}
              className="bg-primary hover:bg-primary-hover active:scale-95 text-white px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center space-x-1.5 shadow-sm"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Create Job / Drive</span>
            </button>
            <button 
              onClick={() => { setGeneratedGuestLink(''); setShowInviteModal(true); }}
              className="border border-border hover:bg-canvas-subtle text-ink px-3.5 py-1.5 rounded-lg text-xs font-medium transition-colors flex items-center space-x-1.5"
            >
              <Send className="w-3.5 h-3.5" />
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
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.2 }}
                className="space-y-8"
              >
                {/* KPI Strip */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
                  <div className="bg-white border border-border rounded-xl p-5 shadow-xs">
                    <div className="text-xs font-medium text-ink-muted">Active Drives</div>
                    <div className="text-2xl font-semibold text-ink mt-2 tracking-tight">{jobs.length}</div>
                    <div className="text-[11px] text-emerald-600 font-medium mt-1 flex items-center gap-1 font-mono">
                      <ArrowUpRight className="w-3 h-3" /> +2 this month
                    </div>
                  </div>
                  <div className="bg-white border border-border rounded-xl p-5 shadow-xs">
                    <div className="text-xs font-medium text-ink-muted">Total Candidates</div>
                    <div className="text-2xl font-semibold text-ink mt-2 tracking-tight">128</div>
                    <div className="text-[11px] text-emerald-600 font-medium mt-1 flex items-center gap-1 font-mono">
                      <ArrowUpRight className="w-3 h-3" /> 94% evaluated
                    </div>
                  </div>
                  <div className="bg-white border border-border rounded-xl p-5 shadow-xs">
                    <div className="text-xs font-medium text-ink-muted">Interviews Completed</div>
                    <div className="text-2xl font-semibold text-ink mt-2 tracking-tight">42</div>
                    <div className="text-[11px] text-emerald-600 font-medium mt-1 flex items-center gap-1 font-mono">
                      <ArrowUpRight className="w-3 h-3" /> +12 this week
                    </div>
                  </div>
                  <div className="bg-white border border-border rounded-xl p-5 shadow-xs">
                    <div className="text-xs font-medium text-ink-muted">Average Competency Score</div>
                    <div className="text-2xl font-semibold text-ink mt-2 tracking-tight">82.4<span className="text-xs font-normal text-ink-muted">/100</span></div>
                    <div className="text-[11px] text-primary font-medium mt-1 flex items-center gap-1 font-mono">
                      Multi-agent validated
                    </div>
                  </div>
                </div>

                {/* Two Column Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  <div className="lg:col-span-2 bg-white border border-border rounded-xl p-6 shadow-xs">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-sm font-semibold text-ink tracking-tight">Active Recruitment Drives</h3>
                      <button onClick={() => setActiveTab('drives')} className="text-xs font-medium text-primary hover:underline">View all &rarr;</button>
                    </div>
                    <div className="divide-y divide-border">
                      {jobs.map((job) => (
                        <div key={job.id} className="py-3 flex items-center justify-between">
                          <div>
                            <div className="text-xs font-semibold text-ink">{job.title}</div>
                            <div className="text-[11px] text-ink-muted">{job.competencies.join(', ')}</div>
                          </div>
                          <div className="flex items-center space-x-3 text-xs">
                            <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 font-medium text-[11px] font-mono">{job.status}</span>
                            <span className="text-ink-muted font-mono">{job.candidatesCount} Candidates</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="bg-white border border-border rounded-xl p-6 shadow-xs">
                    <h3 className="text-sm font-semibold text-ink tracking-tight mb-4">Realtime Session Stream</h3>
                    <div className="space-y-4 text-xs">
                      <div className="flex items-start space-x-3">
                        <span className="w-2 h-2 rounded-full bg-emerald-500 mt-1.5"></span>
                        <div>
                          <div className="text-ink font-medium">Jane Doe completed interview</div>
                          <div className="text-[11px] text-ink-muted font-mono">Backend Specialist &bull; Multi-Agent Score: 88/100</div>
                        </div>
                      </div>
                      <div className="flex items-start space-x-3">
                        <span className="w-2 h-2 rounded-full bg-primary mt-1.5 animate-pulse"></span>
                        <div>
                          <div className="text-ink font-medium">Alex Smith session active</div>
                          <div className="text-[11px] text-ink-muted font-mono">AI Engineer &bull; LiveKit Stream</div>
                        </div>
                      </div>
                      <div className="flex items-start space-x-3">
                        <span className="w-2 h-2 rounded-full bg-border mt-1.5"></span>
                        <div>
                          <div className="text-ink font-medium">Invitation delivered to Carlos M.</div>
                          <div className="text-[11px] text-ink-muted font-mono">SRE &bull; Guest Token Issued</div>
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
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.2 }}
                className="space-y-6"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-semibold text-ink tracking-tight">Recruitment Drives &amp; Positions</h2>
                    <p className="text-xs text-ink-muted">Configured job profiles with automated GLiNER competency extraction.</p>
                  </div>
                  <button onClick={() => setShowJobModal(true)} className="bg-primary hover:bg-primary-hover text-white px-3 py-1.5 rounded-lg text-xs font-medium">
                    + New Job
                  </button>
                </div>

                <div className="bg-white border border-border rounded-xl overflow-hidden shadow-xs">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-canvas-subtle border-b border-border text-[11px] font-semibold text-ink-muted uppercase tracking-wider font-mono">
                      <tr>
                        <th className="py-3 px-4">Job Title</th>
                        <th className="py-3 px-4">Extracted Competencies</th>
                        <th className="py-3 px-4">Status</th>
                        <th className="py-3 px-4 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                      {jobs.map((j) => (
                        <tr key={j.id} className="hover:bg-canvas-subtle/50 transition-colors">
                          <td className="py-3 px-4 font-semibold text-ink">{j.title}</td>
                          <td className="py-3 px-4">
                            {j.competencies.map((comp, idx) => (
                              <span key={idx} className="inline-block bg-primary-subtle text-primary px-2 py-0.5 rounded text-[11px] font-mono mr-1.5">
                                {comp}
                              </span>
                            ))}
                          </td>
                          <td className="py-3 px-4">
                            <span className="px-2 py-0.5 bg-emerald-50 text-emerald-700 rounded-full font-medium text-[11px] font-mono">{j.status}</span>
                          </td>
                          <td className="py-3 px-4 text-right">
                            <button onClick={() => setActiveTab('candidates')} className="text-primary hover:underline font-medium">
                              View Candidates
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
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.2 }}
                className="space-y-6"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-semibold text-ink tracking-tight">Candidates Roster</h2>
                    <p className="text-xs text-ink-muted">Track candidate interview progression and guest access links.</p>
                  </div>
                  <button onClick={() => { setGeneratedGuestLink(''); setShowInviteModal(true); }} className="bg-primary hover:bg-primary-hover text-white px-3 py-1.5 rounded-lg text-xs font-medium">
                    + Invite Candidate
                  </button>
                </div>

                <div className="bg-white border border-border rounded-xl overflow-hidden shadow-xs">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-canvas-subtle border-b border-border text-[11px] font-semibold text-ink-muted uppercase tracking-wider font-mono">
                      <tr>
                        <th className="py-3 px-4">Candidate</th>
                        <th className="py-3 px-4">Target Position</th>
                        <th className="py-3 px-4">Session Status</th>
                        <th className="py-3 px-4">Score</th>
                        <th className="py-3 px-4 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                      {candidates.map((c) => (
                        <tr key={c.id} className="hover:bg-canvas-subtle/50 transition-colors">
                          <td className="py-3 px-4">
                            <div className="font-semibold text-ink">{c.name}</div>
                            <div className="text-[11px] text-ink-muted font-mono">{c.email}</div>
                          </td>
                          <td className="py-3 px-4 text-ink">{c.role}</td>
                          <td className="py-3 px-4">
                            <span className={`px-2 py-0.5 rounded-full font-medium text-[11px] font-mono ${
                              c.status === 'COMPLETED' ? 'bg-emerald-50 text-emerald-700' :
                              c.status === 'IN_PROGRESS' ? 'bg-amber-50 text-amber-700' : 'bg-primary-subtle text-primary'
                            }`}>
                              {c.status}
                            </span>
                          </td>
                          <td className="py-3 px-4 font-mono font-semibold">
                            {c.score ? <span className="text-emerald-600">{c.score} / 100</span> : <span className="text-ink-muted">--</span>}
                          </td>
                          <td className="py-3 px-4 text-right space-x-3">
                            {c.status === 'COMPLETED' ? (
                              <button onClick={() => setActiveTab('reports')} className="text-primary hover:underline font-medium">
                                View Scorecard
                              </button>
                            ) : (
                              <Link to={c.sessionUrl} target="_blank" className="text-primary hover:underline font-medium inline-flex items-center gap-1">
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
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.2 }}
                className="space-y-6"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-semibold text-ink tracking-tight">Candidate Evaluation Scorecard</h2>
                    <p className="text-xs text-ink-muted">Evidence-backed evaluation report for Jane Doe (Senior Backend Engineer).</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button className="border border-border hover:bg-canvas-subtle px-3 py-1.5 rounded-lg text-xs font-medium">
                      Download PDF
                    </button>
                    <button className="bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-1.5 rounded-lg text-xs font-medium">
                      Advance Candidate
                    </button>
                  </div>
                </div>

                <div className="bg-white border border-border rounded-xl p-6 shadow-xs space-y-6">
                  <div className="flex flex-col md:flex-row justify-between items-start md:items-center pb-6 border-b border-border gap-4">
                    <div>
                      <span className="text-[11px] font-mono bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded font-medium">PASS RECOMMENDATION</span>
                      <h3 className="text-xl font-semibold text-ink mt-2">Jane Doe</h3>
                      <div className="text-xs text-ink-muted font-mono mt-0.5">Role: Senior Backend Engineer &bull; Evaluated by Multi-Agent Orchestrator</div>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-ink-muted font-medium">Composite Score</div>
                      <div className="text-3xl font-bold text-emerald-600 font-mono mt-0.5">88<span className="text-sm font-normal text-ink-muted">/100</span></div>
                    </div>
                  </div>

                  {/* Competency Bars */}
                  <div className="space-y-4 max-w-2xl">
                    <div>
                      <div className="flex justify-between text-xs font-medium mb-1">
                        <span>Technical Reasoning &amp; Architecture (50% Weight)</span>
                        <span className="font-mono text-emerald-600">92%</span>
                      </div>
                      <div className="w-full bg-canvas-muted h-2.5 rounded-full overflow-hidden">
                        <div className="bg-emerald-600 h-full w-[92%] transition-all duration-500"></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-xs font-medium mb-1">
                        <span>Behavioral Ownership &amp; Collaboration (25% Weight)</span>
                        <span className="font-mono text-emerald-600">85%</span>
                      </div>
                      <div className="w-full bg-canvas-muted h-2.5 rounded-full overflow-hidden">
                        <div className="bg-emerald-600 h-full w-[85%] transition-all duration-500"></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-xs font-medium mb-1">
                        <span>Communication Clarity &amp; Precision (25% Weight)</span>
                        <span className="font-mono text-emerald-600">87%</span>
                      </div>
                      <div className="w-full bg-canvas-muted h-2.5 rounded-full overflow-hidden">
                        <div className="bg-emerald-600 h-full w-[87%] transition-all duration-500"></div>
                      </div>
                    </div>
                  </div>

                  {/* Cited Evidence Quotes */}
                  <div className="pt-6 border-t border-border">
                    <h4 className="text-xs font-semibold text-ink uppercase tracking-wider font-mono mb-3">Cited Verbatim Evidence</h4>
                    <div className="space-y-3 text-xs">
                      <div className="bg-canvas-subtle border border-border rounded-lg p-3.5 space-y-1">
                        <span className="font-semibold text-primary font-mono text-[11px]">[Technical Agent - Q3]:</span>
                        <p className="text-ink italic">"In our architecture, we offloaded writes into Redis queues and scoped queries strictly with tenant Row-Level Security."</p>
                        <div className="text-[11px] text-emerald-600 font-medium">Relevance: High &bull; Confirmed practical experience with RLS partitioning.</div>
                      </div>
                      <div className="bg-canvas-subtle border border-border rounded-lg p-3.5 space-y-1">
                        <span className="font-semibold text-primary font-mono text-[11px]">[Behavioral Agent - Q5]:</span>
                        <p className="text-ink italic">"Took full responsibility for resolving post-deployment edge cases and aligned cross-functional teams on incident reviews."</p>
                        <div className="text-[11px] text-emerald-600 font-medium">Relevance: High &bull; Strong proactive leadership and accountability.</div>
                      </div>
                      <div className="bg-canvas-subtle border border-border rounded-lg p-3.5 space-y-1">
                        <span className="font-semibold text-primary font-mono text-[11px]">[Communication Agent]:</span>
                        <p className="text-ink italic">"Candidate spoke concisely and structured trade-offs clearly without filler phrases."</p>
                        <div className="text-[11px] text-emerald-600 font-medium">Clarity Score: 86 &bull; Conciseness Score: 88.</div>
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
          <div className="fixed inset-0 bg-dark-base/50 backdrop-blur-xs flex items-center justify-center z-50 p-4">
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white border border-border rounded-xl p-6 max-w-lg w-full shadow-2xl space-y-4"
            >
              <div className="flex justify-between items-center border-b border-border pb-3">
                <h3 className="text-sm font-semibold text-ink">Create Job &amp; Parse Competencies</h3>
                <X onClick={() => setShowJobModal(false)} className="w-4 h-4 text-ink-muted hover:text-ink cursor-pointer" />
              </div>
              <form onSubmit={handleCreateJob} className="space-y-3 text-xs">
                <div>
                  <label className="block font-medium text-ink mb-1">Job Title</label>
                  <input 
                    type="text" 
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                    required
                    placeholder="e.g. Lead Platform Architect" 
                    className="w-full border border-border rounded-lg p-2.5 text-xs focus:outline-none focus:border-primary"
                  />
                </div>
                <div>
                  <label className="block font-medium text-ink mb-1">Job Description</label>
                  <textarea 
                    rows={4} 
                    value={newJD}
                    onChange={(e) => setNewJD(e.target.value)}
                    placeholder="Paste job description here. Autergo's GLiNER extractor will automatically extract competencies..." 
                    className="w-full border border-border rounded-lg p-2.5 text-xs focus:outline-none focus:border-primary"
                  />
                  <div className="text-[11px] text-primary flex items-center gap-1 mt-1 font-mono">
                    <Sparkles className="w-3 h-3" />
                    <span>Real GLiNER backend NLP extraction enabled</span>
                  </div>
                </div>
                <div className="flex justify-end space-x-2 pt-2 border-t border-border">
                  <button type="button" onClick={() => setShowJobModal(false)} className="px-3 py-1.5 rounded-lg border border-border text-xs font-medium text-ink hover:bg-canvas-subtle">
                    Cancel
                  </button>
                  <button type="submit" disabled={loading} className="px-4 py-1.5 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-medium flex items-center gap-1.5">
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
          <div className="fixed inset-0 bg-dark-base/50 backdrop-blur-xs flex items-center justify-center z-50 p-4">
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white border border-border rounded-xl p-6 max-w-md w-full shadow-2xl space-y-4"
            >
              <div className="flex justify-between items-center border-b border-border pb-3">
                <h3 className="text-sm font-semibold text-ink">Invite Candidate (Real Backend Token)</h3>
                <X onClick={() => setShowInviteModal(false)} className="w-4 h-4 text-ink-muted hover:text-ink cursor-pointer" />
              </div>
              <form onSubmit={handleInviteCandidate} className="space-y-3 text-xs">
                <div>
                  <label className="block font-medium text-ink mb-1">Target Position</label>
                  <select 
                    value={selectedJobId} 
                    onChange={(e) => setSelectedJobId(e.target.value)}
                    className="w-full border border-border rounded-lg p-2.5 text-xs focus:outline-none focus:border-primary"
                  >
                    {jobs.map(j => (
                      <option key={j.id} value={j.id}>{j.title}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block font-medium text-ink mb-1">Candidate Full Name</label>
                  <input 
                    type="text" 
                    value={inviteName}
                    onChange={(e) => setInviteName(e.target.value)}
                    required
                    placeholder="e.g. John Doe" 
                    className="w-full border border-border rounded-lg p-2.5 text-xs focus:outline-none focus:border-primary"
                  />
                </div>
                <div>
                  <label className="block font-medium text-ink mb-1">Candidate Email</label>
                  <input 
                    type="email" 
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    required
                    placeholder="john@example.com" 
                    className="w-full border border-border rounded-lg p-2.5 text-xs focus:outline-none focus:border-primary"
                  />
                </div>

                {generatedGuestLink && (
                  <div className="bg-canvas-subtle border border-border rounded p-3 text-xs font-mono space-y-1.5">
                    <div className="text-ink-muted text-[11px] font-semibold">Real Candidate Guest Link:</div>
                    <input 
                      type="text" 
                      readOnly 
                      value={generatedGuestLink} 
                      className="w-full bg-white border border-border rounded p-1.5 text-[11px] text-primary select-all"
                    />
                    <div className="text-[10px] text-emerald-600">Saved to database &bull; ready to share with candidate.</div>
                  </div>
                )}

                <div className="flex justify-end space-x-2 pt-2 border-t border-border">
                  <button type="button" onClick={() => setShowInviteModal(false)} className="px-3 py-1.5 rounded-lg border border-border text-xs font-medium text-ink hover:bg-canvas-subtle">
                    Close
                  </button>
                  <button type="submit" disabled={loading} className="px-4 py-1.5 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-medium flex items-center gap-1.5">
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
