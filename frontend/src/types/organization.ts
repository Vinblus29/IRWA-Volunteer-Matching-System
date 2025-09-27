export interface Organization {
  id: string;
  name: string;
  email: string;
  phone?: string;
  website?: string;
  mission_statement: string;
  description: string;
  founded_year?: number;
  size: string;
  focus_areas: string[];
  address: any;
  contact_person: any;
  is_verified: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  created_by?: string;
  rating?: number;
  total_events?: number;
  total_volunteers?: number;
  total_hours?: number;
}

export interface OrganizationCreate {
  name: string;
  email: string;
  phone?: string;
  website?: string;
  mission_statement: string;
  description: string;
  founded_year?: number;
  size: string;
  focus_areas: string[];
  address: any;
  contact_person: any;
}

export interface OrganizationUpdate {
  name?: string;
  email?: string;
  phone?: string;
  website?: string;
  mission_statement?: string;
  description?: string;
  founded_year?: number;
  size?: string;
  focus_areas?: string[];
  address?: any;
  contact_person?: any;
  is_active?: boolean;
}
