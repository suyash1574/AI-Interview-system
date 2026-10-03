/**
 * Autergo Central API Client
 * Wraps backend FastAPI REST endpoints with authentication and error handling.
 */

const BASE_URL = '/api/v1';

// In development or when using mock token, attach fallback bearer
function getAuthHeaders() {
  const token = localStorage.getItem('autergo_token') || 'dev_mock_jwt_token';
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };
}

export const api = {
  // Jobs
  async getJobs() {
    try {
      const res = await fetch(`${BASE_URL}/jobs`, { headers: getAuthHeaders() });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (e) {
      console.warn('API getJobs failed, falling back to local state:', e);
      return null;
    }
  },

  async createJob(title, descriptionText) {
    const res = await fetch(`${BASE_URL}/jobs`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ title, description_text: descriptionText })
    });
    if (!res.ok) throw new Error(`Failed to create job: HTTP ${res.status}`);
    return await res.json();
  },

  // Drives
  async getDrives() {
    try {
      const res = await fetch(`${BASE_URL}/drives`, { headers: getAuthHeaders() });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (e) {
      console.warn('API getDrives failed:', e);
      return null;
    }
  },

  async createDrive(name, jobId, passThreshold = 70) {
    const res = await fetch(`${BASE_URL}/drives`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ name, job_id: jobId, pass_threshold: passThreshold })
    });
    if (!res.ok) throw new Error(`Failed to create drive: HTTP ${res.status}`);
    return await res.json();
  },

  // Interviews & Candidates
  async createInterview(jobId, candidateName, candidateEmail) {
    const res = await fetch(`${BASE_URL}/interviews`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        job_id: jobId,
        candidate_name: candidateName,
        candidate_email: candidateEmail
      })
    });
    if (!res.ok) throw new Error(`Failed to schedule interview: HTTP ${res.status}`);
    return await res.json();
  },

  async getInterview(interviewId) {
    const res = await fetch(`${BASE_URL}/interviews/${interviewId}`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  },

  // Evaluations
  async getEvaluation(interviewId) {
    const res = await fetch(`${BASE_URL}/evaluations/${interviewId}`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  },

  // Resumes
  async uploadResume(candidateId, interviewId, file) {
    const formData = new FormData();
    formData.append('candidate_id', candidateId);
    if (interviewId) formData.append('interview_id', interviewId);
    formData.append('file', file);

    const token = localStorage.getItem('autergo_token') || 'dev_mock_jwt_token';
    const res = await fetch(`${BASE_URL}/resumes/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });
    if (!res.ok) throw new Error(`Failed to upload resume: HTTP ${res.status}`);
    return await res.json();
  }
};
