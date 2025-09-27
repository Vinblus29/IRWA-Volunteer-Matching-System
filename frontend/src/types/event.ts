export interface Event {
  id: string;
  title: string;
  description: string;
  organization_id: string;
  organization_name?: string;
  event_type: string;
  start_date: string;
  end_date: string;
  start_time: string;
  end_time: string;
  location: any;
  max_volunteers: number;
  current_volunteers: number;
  required_skills: string[];
  preferred_skills?: string[];
  status: string;
  created_at: string;
  updated_at: string;
  created_by: string;
  tags?: string[];
  difficulty_level?: string;
  commitment_hours?: number;
  is_remote?: boolean;
  requirements?: string[];
  benefits?: string[];
  contact_email?: string;
  contact_phone?: string;
  image_url?: string;
  external_url?: string;
}

export interface EventCreate {
  title: string;
  description: string;
  organization_id: string;
  event_type: string;
  start_date: string;
  end_date: string;
  start_time: string;
  end_time: string;
  location: any;
  max_volunteers: number;
  required_skills: string[];
  preferred_skills?: string[];
  tags?: string[];
  difficulty_level?: string;
  commitment_hours?: number;
  is_remote?: boolean;
  requirements?: string[];
  benefits?: string[];
  contact_email?: string;
  contact_phone?: string;
  image_url?: string;
  external_url?: string;
}

export interface EventUpdate {
  title?: string;
  description?: string;
  event_type?: string;
  start_date?: string;
  end_date?: string;
  start_time?: string;
  end_time?: string;
  location?: any;
  max_volunteers?: number;
  required_skills?: string[];
  preferred_skills?: string[];
  status?: string;
  tags?: string[];
  difficulty_level?: string;
  commitment_hours?: number;
  is_remote?: boolean;
  requirements?: string[];
  benefits?: string[];
  contact_email?: string;
  contact_phone?: string;
  image_url?: string;
  external_url?: string;
}
