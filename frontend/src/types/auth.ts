export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  phone?: string;
  role: 'volunteer' | 'organization' | 'admin';
  is_active: boolean;
  created_at: string;
  updated_at: string;
  last_login?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  full_name: string;
  phone?: string;
  password: string;
  role: 'volunteer' | 'organization';
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface PasswordChangeData {
  current_password: string;
  new_password: string;
}

export interface ForgotPasswordData {
  email: string;
}

export interface ResetPasswordData {
  token: string;
  new_password: string;
}

export interface UserUpdateData {
  email?: string;
  username?: string;
  full_name?: string;
  phone?: string;
} 