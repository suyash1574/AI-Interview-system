import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api/client';

export default function DriveCreatePage() {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState([]);
  const [name, setName] = useState('');
  const [jobId, setJobId] = useState('');
  const [passThreshold, setPassThreshold] = useState(70);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadJobs() {
      const data = await api.getJobs();
      if (data && Array.isArray(data)) {
        setJobs(data);
        if (data.length > 0) setJobId(data[0].id);
      }
    }
    loadJobs();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) {
      setError('Please provide a drive name');
      return;
    }
    setSubmitting(true);
    setError(null);

    try {
      await api.createDrive(name, jobId || 'job-default', passThreshold);
      navigate('/drives');
    } catch (err) {
      setError(err.message || 'Failed to create drive');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-6">
          <Link to="/" className="text-xl font-bold tracking-tight bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">
            AUTERGO
          </Link>
          <nav className="flex space-x-4 text-sm font-medium text-slate-400">
            <Link to="/dashboard" className="hover:text-slate-200 transition">Overview</Link>
            <Link to="/drives" className="text-blue-400">Hiring Drives</Link>
          </nav>
        </div>
      </header>

      <main className="flex-1 max-w-3xl w-full mx-auto p-6 md:p-8 space-y-6">
        <div className="space-y-1">
          <h1 className="text-2xl font-bold tracking-tight">Create New Hiring Drive</h1>
          <p className="text-slate-400 text-sm">Launch a targeted technical evaluation campaign for a specific engineering role.</p>
        </div>

        {error && (
          <div className="p-4 bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm rounded-lg">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="bg-slate-900/40 border border-slate-800 rounded-xl p-6 space-y-6 shadow-xl">
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Drive Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. 2026 Q4 Senior Full-Stack Engineering Drive"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-blue-500 transition"
              required
            />
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Target Job Profile</label>
            <select
              value={jobId}
              onChange={(e) => setJobId(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-blue-500 transition"
            >
              {jobs.length > 0 ? (
                jobs.map((j) => (
                  <option key={j.id} value={j.id}>
                    {j.title} ({j.competencies?.length || 0} competencies)
                  </option>
                ))
              ) : (
                <option value="job-default">Senior Backend Engineer (Default)</option>
              )}
            </select>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Pass Benchmark Threshold</label>
              <span className="font-mono text-sm text-blue-400 font-semibold">{passThreshold}%</span>
            </div>
            <input
              type="range"
              min="50"
              max="95"
              step="5"
              value={passThreshold}
              onChange={(e) => setPassThreshold(Number(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
            <p className="text-xs text-slate-500">Candidates scoring at or above this threshold receive automated PASS recommendations.</p>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
            <Link
              to="/drives"
              className="px-4 py-2 text-sm text-slate-400 hover:text-slate-200 transition"
            >
              Cancel
            </Link>
            <button
              type="submit"
              disabled={submitting}
              className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-sm font-semibold px-6 py-2 rounded-lg shadow-lg shadow-blue-500/20 transition"
            >
              {submitting ? 'Creating Drive...' : 'Launch Drive'}
            </button>
          </div>
        </form>
      </main>
    </div>
  );
}
