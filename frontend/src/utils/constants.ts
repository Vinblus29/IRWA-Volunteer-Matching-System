export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const ROUTES = {
  HOME: "/",
  LOGIN: "/login",
  REGISTER: "/register",
  DASHBOARD: "/dashboard",
  PROFILE: "/profile",
  EVENTS: "/events",
  EVENT_DETAIL: "/events/:id",
  CREATE_EVENT: "/events/create",
  MATCHING: "/matching",
  MESSAGES: "/messages",
  SETTINGS: "/settings",
} as const;

export const USER_ROLES = {
  VOLUNTEER: "volunteer",
  ORGANIZATION: "organization",
  ADMIN: "admin",
} as const;

export const MATCH_STATUSES = {
  PENDING: "pending",
  ACCEPTED: "accepted",
  DECLINED: "declined",
  COMPLETED: "completed",
} as const;

export const EVENT_STATUSES = {
  DRAFT: "draft",
  ACTIVE: "active",
  CANCELLED: "cancelled",
  COMPLETED: "completed",
} as const;

export const EVENT_CATEGORIES = [
  "Environmental",
  "Education",
  "Healthcare",
  "Community",
  "Animal Welfare",
  "Social Services",
  "Arts & Culture",
  "Sports & Recreation",
  "Technology",
  "Disaster Relief",
] as const;

export const SKILL_LEVELS = [
  "beginner",
  "intermediate",
  "advanced",
  "expert",
] as const;

export const COMMITMENT_LEVELS = [
  "low",
  "medium",
  "high",
] as const;

export const DAYS_OF_WEEK = [
  "monday",
  "tuesday",
  "wednesday",
  "thursday",
  "friday",
  "saturday",
  "sunday",
] as const;

export const NOTIFICATION_TYPES = {
  SUCCESS: "success",
  ERROR: "error",
  WARNING: "warning",
  INFO: "info",
} as const;

export const LOCAL_STORAGE_KEYS = {
  AUTH_TOKEN: "auth_token",
  USER_PREFERENCES: "user_preferences",
  THEME_MODE: "theme_mode",
} as const;

export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
} as const;

export const VALIDATION_RULES = {
  PASSWORD_MIN_LENGTH: 8,
  EMAIL_REGEX: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
  PHONE_REGEX: /^\+?[\d\s\-\(\)]+$/,
  MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB
  ALLOWED_IMAGE_TYPES: ["image/jpeg", "image/png", "image/gif"],
  ALLOWED_DOCUMENT_TYPES: ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
} as const;

export const AI_FEATURES = {
  MIN_MATCH_SCORE: 0.3,
  GOOD_MATCH_THRESHOLD: 0.7,
  EXCELLENT_MATCH_THRESHOLD: 0.9,
  MAX_SUGGESTIONS: 10,
} as const;

export const THEME_COLORS = {
  PRIMARY: "#667eea",
  SECONDARY: "#764ba2",
  SUCCESS: "#4caf50",
  WARNING: "#ff9800",
  ERROR: "#f44336",
  INFO: "#2196f3",
} as const;
