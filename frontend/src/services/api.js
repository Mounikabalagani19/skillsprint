import axios from "axios";

// Use environment variable or fallback to localhost for development
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

const apiClient = axios.create({
  baseURL: API_BASE,
});

// Interceptor to add the auth token to every request
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default {
  getChallenges() {
    return apiClient.get("/challenges/");
  },

  createUser(userData) {
    return apiClient.post("/users/", userData);
  },

  loginUser(formData) {
    return apiClient.post("/users/token", formData, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });
  },

  loginGuest() {
    return apiClient.post("/users/guest-token");
  },

  submitAnswer(challengeId, answer) {
    return apiClient.post(`/challenges/${challengeId}/submit`, { answer });
  },

  getLeaderboard() {
    return apiClient.get("/leaderboard/");
  },

  // --- NEW FUNCTION TO GET USER'S OWN DATA ---
  getMe() {
    return apiClient.get('/users/me');
  },

  // --- Modules ---
  listModuleLevels() {
    return apiClient.get('/modules/levels');
  },

  getModuleItems(level, module = 'python') {
    if (module && module !== 'python') return apiClient.get(`/modules/${module}/${level}`);
    return apiClient.get(`/modules/${level}`); // back-compat
  },

  submitModuleAnswer(level, payload, module = 'python') {
    if (module && module !== 'python') return apiClient.post(`/modules/${module}/${level}/submit`, payload);
    return apiClient.post(`/modules/${level}/submit`, payload); // back-compat
  },

  getCustomModuleItems(moduleId) {
    return apiClient.get(`/modules/custom/${moduleId}`);
  },

  submitCustomModuleAnswer(moduleId, payload) {
    return apiClient.post(`/modules/custom/${moduleId}/submit`, payload);
  },

  getAnnouncements() {
    return apiClient.get("/announcements/");
  },

  createAnnouncement(content) {
    return apiClient.post("/announcements/", { content });
  },

  getMentorStudents() {
    return apiClient.get("/management/mentor/students");
  },

  getAdminStats() {
    return apiClient.get("/management/admin/stats");
  },

  uploadChallenges(challenges) {
    return apiClient.post("/management/mentor/challenges", challenges);
  },

  // --- Analytics ---
  getStudentPerformance() {
    return apiClient.get('/analytics/student-performance');
  },

  getActivityTimeline(days = 7) {
    return apiClient.get(`/analytics/activity-timeline?days=${days}`);
  },

  // --- Custom Modules (PDF generated) ---
  uploadPdfModule(formData) {
    return apiClient.post('/management/mentor/modules/pdf', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  saveCustomModule(payload) {
    return apiClient.post('/management/mentor/modules/save', payload);
  },

  listCustomModules() {
    return apiClient.get('/management/modules/custom');
  },

  getCustomModule(moduleId) {
    return apiClient.get(`/management/modules/custom/${moduleId}`);
  },

  deleteCustomModule(moduleId) {
    return apiClient.delete(`/management/modules/custom/${moduleId}`);
  },

  // --- Daily Challenges management ---
  getAllChallengesAdmin() {
    return apiClient.get('/management/mentor/challenges/all');
  },

  createChallengeManual(data) {
    return apiClient.post('/management/mentor/challenges/single', data);
  },

  updateChallenge(id, data) {
    return apiClient.put(`/management/mentor/challenges/${id}`, data);
  },

  deleteChallenge(id) {
    return apiClient.delete(`/management/mentor/challenges/${id}`);
  },

  toggleChallengeActive(id) {
    return apiClient.patch(`/management/mentor/challenges/${id}/toggle`);
  },
};

