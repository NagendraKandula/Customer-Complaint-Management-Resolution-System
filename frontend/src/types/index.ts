// Types mirror the PostgreSQL schema column names. Because the exact JSON
// envelope of each endpoint is unknown at build time, every field is optional
// and the services layer normalises responses defensively.

export type Dict = Record<string, any>;

export interface Complaint {
  complaint_id: number | string;
  customer_id?: number | string;
  order_id?: number | string;
  product_id?: number | string;
  category_id?: number | string;
  priority_rule_id?: number | string;
  complaint_text?: string;
  channel?: string;
  sentiment?: string | number;
  severity?: string | number;
  priority?: string;
  priority_score?: number;
  class_rule_fired?: string;
  is_safety_related?: boolean;
  is_repeat?: boolean;
  repeat_of_complaint_id?: number | string | null;
  status?: string;
  reopen_count?: number;
  closed_at?: string | null;
  created_at?: string;
  updated_at?: string;
  customer_name?: string;
  full_name?: string;
  [key: string]: any;
}

export interface DistributionItem {
  name: string;
  value: number;
}

export interface SummaryStats {
  total?: number;
  open?: number;
  resolved?: number;
  closed?: number;
  reopened?: number;
}

export interface SlaStats {
  total?: number;
  responseBreaches?: number;
  resolutionBreaches?: number;
  compliant?: number;
  paused?: number;
}

export interface AgentRow {
  name: string;
  total?: number;
  current?: number;
}

export interface AgentStats {
  totalAssignments?: number;
  currentAssignments?: number;
  agents: AgentRow[];
}

export interface ComplaintFilters {
  page: number;
  pageSize: number;
  search?: string;
  status?: string;
  priority?: string;
  severity?: string;
  channel?: string;
}

export interface Paged<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

export interface ComplaintDetailsModel {
  complaint: Complaint;
  customer: Dict | null;
  messages: Dict[];
  history: Dict[];
  assignments: Dict[];
  resolutions: Dict[];
  slaClocks: Dict[];
  slaEvents: Dict[];
  surveys: Dict[];
  raw: unknown;
}
