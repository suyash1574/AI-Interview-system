import React from 'react';
import { Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage.jsx';
import RecruiterLogin from './pages/RecruiterLogin.jsx';
import RecruiterDashboard from './pages/RecruiterDashboard.jsx';
import CandidateCheckin from './pages/CandidateCheckin.jsx';
import VoiceInterviewShell from './pages/VoiceInterviewShell.jsx';
import DriveListPage from './pages/DriveListPage.jsx';
import DriveCreatePage from './pages/DriveCreatePage.jsx';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<RecruiterLogin />} />
      <Route path="/dashboard" element={<RecruiterDashboard />} />
      <Route path="/drives" element={<DriveListPage />} />
      <Route path="/drives/new" element={<DriveCreatePage />} />
      <Route path="/checkin" element={<CandidateCheckin />} />
      <Route path="/interview/:sessionId" element={<VoiceInterviewShell />} />
      <Route path="/interview" element={<VoiceInterviewShell />} />
    </Routes>
  );
}
