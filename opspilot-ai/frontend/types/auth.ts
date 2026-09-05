export type Role = "admin" | "manager" | "viewer";

export interface Organization {
  id: number;
  name: string;
  created_at: string;
}

export interface Membership {
  organization: Organization;
  role: Role;
}

export interface CurrentUser {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
  memberships: Membership[];
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}
