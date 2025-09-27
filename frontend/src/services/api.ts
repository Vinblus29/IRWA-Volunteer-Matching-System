import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
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

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: async (credentials: { email: string; password: string }) => {
    const response = await api.post("/api/auth/login", credentials);
    return response.data;
  },
  register: async (userData: any) => {
    const response = await api.post("/api/auth/register", userData);
    return response.data;
  },
  logout: async () => {
    const response = await api.post("/api/auth/logout");
    return response.data;
  },
  getProfile: async () => {
    const response = await api.get("/api/auth/profile");
    return response.data;
  },
  setAuthToken: (token: string) => {
    localStorage.setItem("token", token);
  },
  removeAuthToken: () => {
    localStorage.removeItem("token");
  },
  getCurrentUser: async () => {
    const response = await api.get("/api/auth/me");
    return response.data;
  },
};

export const volunteerAPI = {
  getProfile: async () => {
    const response = await api.get("/api/volunteers/profile");
    return response.data;
  },
  getMyProfile: async () => {
    const response = await api.get("/api/volunteers/profile");
    return response.data;
  },
  updateProfile: async (data: any) => {
    const response = await api.put("/api/volunteers/profile", data);
    return response.data;
  },
  getSkills: async () => {
    const response = await api.get("/api/volunteers/skills");
    return response.data;
  },
  updateSkills: async (skills: any) => {
    const response = await api.put("/api/volunteers/skills", skills);
    return response.data;
  },
  getStats: async () => {
    const response = await api.get("/api/volunteers/stats");
    return response.data;
  },
};

export const volunteersAPI = volunteerAPI; // Alias for compatibility

export const eventAPI = {
  getEvents: async (filters?: any) => {
    const response = await api.get("/api/events", { params: filters });
    return response.data;
  },
  getEvent: async (id: string) => {
    const response = await api.get(`/api/events/${id}`);
    return response.data;
  },
  createEvent: async (eventData: any) => {
    const response = await api.post("/api/events", eventData);
    return response.data;
  },
  updateEvent: async (id: string, eventData: any) => {
    const response = await api.put(`/api/events/${id}`, eventData);
    return response.data;
  },
  deleteEvent: async (id: string) => {
    const response = await api.delete(`/api/events/${id}`);
    return response.data;
  },
};

export const eventsAPI = eventAPI; // Alias for compatibility

export const matchingAPI = {
  findMatches: async (filters?: any) => {
    const response = await api.post("/api/matching/find-matches", filters);
    return response.data;
  },
  getMatches: async (filters?: any) => {
    const response = await api.get("/api/matching/matches", { params: filters });
    return response.data;
  },
  acceptMatch: async (matchId: string) => {
    const response = await api.post(`/api/matching/matches/${matchId}/accept`);
    return response.data;
  },
  rejectMatch: async (matchId: string) => {
    const response = await api.post(`/api/matching/matches/${matchId}/reject`);
    return response.data;
  },
  declineMatch: async (matchId: string, reason: string) => {
    const response = await api.post(`/api/matching/matches/${matchId}/decline`, { reason });
    return response.data;
  },
};

export const availabilityAPI = {
  getAvailability: async () => {
    const response = await api.get("/api/availability");
    return response.data;
  },
  updateAvailability: async (availability: any) => {
    const response = await api.put("/api/availability", availability);
    return response.data;
  },
  addAvailability: async (availability: any) => {
    const response = await api.post("/api/availability", availability);
    return response.data;
  },
  deleteAvailability: async (id: string) => {
    const response = await api.delete(`/api/availability/${id}`);
    return response.data;
  },
};

export const dashboardAPI = {
  getStats: async () => {
    const response = await api.get("/api/dashboard/stats");
    return response.data;
  },
  getVolunteerDashboard: async () => {
    const response = await api.get("/api/dashboard/volunteer");
    return response.data;
  },
  getRecentActivity: async () => {
    const response = await api.get("/api/dashboard/activity");
    return response.data;
  },
};

export const skillProfilerAPI = {
  analyzeSkills: async (skills: any) => {
    const response = await api.post("/api/skill-profiler/analyze", skills);
    return response.data;
  },
  getSkillTaxonomy: async () => {
    const response = await api.get("/api/skill-profiler/taxonomy");
    return response.data;
  },
  updateSkills: async (skills: any) => {
    const response = await api.put("/api/skill-profiler/skills", skills);
    return response.data;
  },
  getSkillTrends: async () => {
    const response = await api.get("/api/skill-profiler/trends");
    return response.data;
  },
  analyzeText: async (data: any) => {
    const response = await api.post("/api/skill-profiler/analyze-text", data);
    return response.data;
  },
  matchSkills: async (data: any) => {
    const response = await api.post("/api/skill-profiler/match-skills", data);
    return response.data;
  },
  analyzeGaps: async (data: any) => {
    const response = await api.post("/api/skill-profiler/analyze-gaps", data);
    return response.data;
  },
};

export const eventMatcherAPI = {
  findMatches: async (filters?: any) => {
    const response = await api.post("/api/event-matcher/find-matches", filters);
    return response.data;
  },
  findVolunteers: async (filters?: any) => {
    const response = await api.post("/api/event-matcher/find-volunteers", filters);
    return response.data;
  },
  findEvents: async (filters?: any) => {
    const response = await api.post("/api/event-matcher/find-events", filters);
    return response.data;
  },
  getMatchingStats: async (time_period?: string) => {
    const response = await api.get("/api/event-matcher/matching-stats", {
      params: { time_period }
    });
    return response.data;
  },
  explainMatch: async (data: any) => {
    const response = await api.post("/api/event-matcher/explain-match", data);
    return response.data;
  },
};

export default api;
