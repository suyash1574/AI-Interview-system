import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { api } from '../api/client';

export default function DriveListPage() {
  const [drives, setDrives] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDrive, setSelectedDrive] = useState(null);
  const [csvFile, setCsvFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(null);

  useEffect(() => {
    fetchDrives();
  }, []);

  const fetchDrives = async () => {
    setLoading(true);
    const data = await api.getDrives();
    if (data && Array.isArray(data)) {
      setDrives(data);
    } else {
      // Demo fallback
      setDrives([
        {
          id: 'drv-demo-1',
          name: 'Q4 Senior Backend Campus Drive',
          status: 'ACTIVE',
          pass_threshold: 75,
          candidate_count: 18,
          completed_count: 12,
          created_at: new Date().toISOString()
        }
      ]);
    }
    setLoading(false);
  };

  const handleStatusToggle = async (driveId, currentStatus) => {
    const nextStatus = currentStatus === 'ACTIVE' ? 'PAUSED' : 'ACTIVE';
    try {
      await api.updateDriveStatus(driveId, nextStatus);
      fetchDrives();
    } catch (e) {
      console.error('Failed to update status', e);
    }
  };

  const handleBulkCsvSubmit = async (e) => {
    e.preventDefault();
    if (!csvFile || !selectedDrive) return;

    setUploading(true);
    try {
      const res = await api.uploadBulkCsv(selectedDrive.id, csvFile);
      setUploadSuccess(`Successfully invited ${res.invited_count} candidate(s)!`);
      setCsvFile(null);
      setTimeout(() => {
        setSelectedDrive(null);
        setUploadSuccess(null);
        fetchDrives();
      }, 2000);
    } catch (e) {
      alert(`Bulk upload failed: ${e.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navigation */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur px-6 py-4 flex items-center justify-between sticky top-0 z-40">
        <div className="flex items-center space-x-6">
          <Link to="/" className="text-xl font-bold tracking-tight bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">
            AUTERGO
          </Link>
          <nav className="flex space-x-4 text-sm font-medium text-slate-400">
            <Link to="/dashboard" className="hover:text-slate-200 transition">Overview</Link>
            <Link to="/drives" className="text-blue-400">Hiring Drives</Link>
          </nav>
        </div>
        <div className="flex items-center space-x-3">
          <Link
            to="/drives/new"
            className="bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold px-4 py-2 rounded-lg shadow-lg shadow-blue-500/20 transition flex items-center gap-2"
          >
            <span>+</span> Create Drive
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 md:p-8 space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Hiring Drives Management</h1>
            <p className="text-slate-400 text-sm">Orchestrate batch candidate recruitment campaigns and bulk invitations.</p>
          </div>
        </div>

        {/* Drives Table */}
        <div className="bg-slate-900/40 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
          {loading ? (
            <div className="p-12 text-center text-slate-500">Loading active hiring drives...</div>
          ) : drives.length === 0 ? (
            <div className="p-12 text-center space-y-3">
              <p className="text-slate-400">No hiring drives found for this organization.</p>
              <Link to="/drives/new" className="inline-block text-blue-400 hover:underline text-sm font-medium">Create your first drive →</Link>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-sm">
                <thead>
                  <tr className="border-b border-slate-800 bg-slate-900/80 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    <th className="py-4 px-6">Drive Name</th>
                    <th className="py-4 px-6">Status</th>
                    <th className="py-4 px-6">Threshold</th>
                    <th className="py-4 px-6">Invited</th>
                    <th className="py-4 px-6">Completed</th>
                    <th className="py-4 px-6 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {drives.map((d) => (
                    <motion.tr
                      key={d.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="hover:bg-slate-800/30 transition"
                    >
                      <td className="py-4 px-6 font-medium text-slate-200">
                        {d.name}
                        <div className="text-xs text-slate-500">ID: {d.id}</div>
                      </td>
                      <td className="py-4 px-6">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                          d.status === 'ACTIVE'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : d.status === 'PAUSED'
                            ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                            : 'bg-slate-500/10 text-slate-400 border border-slate-500/20'
                        }`}>
                          {d.status}
                        </span>
                      </td>
                      <td className="py-4 px-6 text-slate-300 font-mono">{d.pass_threshold}%</td>
                      <td className="py-4 px-6 text-slate-300 font-mono">{d.candidate_count || 0}</td>
                      <td className="py-4 px-6 text-slate-300 font-mono">{d.completed_count || 0}</td>
                      <td className="py-4 px-6 text-right space-x-2">
                        <button
                          onClick={() => handleStatusToggle(d.id, d.status)}
                          className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-lg border border-slate-700 transition"
                        >
                          {d.status === 'ACTIVE' ? 'Pause' : 'Activate'}
                        </button>
                        <button
                          onClick={() => setSelectedDrive(d)}
                          className="text-xs bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 px-3 py-1.5 rounded-lg border border-blue-500/30 transition"
                        >
                          Bulk Invite (CSV)
                        </button>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Bulk Invite Modal */}
        {selectedDrive && (
          <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="bg-slate-900 border border-slate-800 rounded-xl max-w-lg w-full p-6 space-y-5 shadow-2xl"
            >
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-lg font-bold text-slate-100">Bulk Invite Candidates</h3>
                  <p className="text-xs text-slate-400">Target Drive: {selectedDrive.name}</p>
                </div>
                <button
                  onClick={() => setSelectedDrive(null)}
                  className="text-slate-400 hover:text-slate-200 text-xl font-bold"
                >
                  ×
                </button>
              </div>

              {uploadSuccess ? (
                <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm rounded-lg text-center font-medium">
                  {uploadSuccess}
                </div>
              ) : (
                <form onSubmit={handleBulkCsvSubmit} className="space-y-4">
                  <div className="p-4 border-2 border-dashed border-slate-700 hover:border-blue-500 rounded-xl text-center space-y-2 cursor-pointer transition">
                    <input
                      type="file"
                      accept=".csv"
                      onChange={(e) => setCsvFile(e.target.files[0])}
                      className="hidden"
                      id="bulk-csv-input"
                    />
                    <label htmlFor="bulk-csv-input" className="cursor-pointer block">
                      <div className="text-2xl text-blue-400 mb-1">📄</div>
                      <p className="text-sm font-medium text-slate-200">
                        {csvFile ? csvFile.name : 'Click to select candidates CSV'}
                      </p>
                      <p className="text-xs text-slate-500">Columns required: Name, Email (and optional Phone)</p>
                    </label>
                  </div>

                  <div className="flex justify-end gap-3 pt-2">
                    <button
                      type="button"
                      onClick={() => setSelectedDrive(null)}
                      className="px-4 py-2 text-sm text-slate-400 hover:text-slate-200 rounded-lg"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={!csvFile || uploading}
                      className="px-4 py-2 text-sm bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold rounded-lg shadow-lg shadow-blue-500/20 transition"
                    >
                      {uploading ? 'Dispatching Invites...' : 'Upload & Send Invites'}
                    </button>
                  </div>
                </form>
              )}
            </motion.div>
          </div>
        )}
      </main>
    </div>
  );
}
