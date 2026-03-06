import { apiGet } from './client';

export interface ReportSummary {
  total_assets: number;
  active_assets: number;
  total_repairs: number;
  maintenance_plans: number;
  verification_scans: number;
}

export function getSummary() {
  return apiGet<ReportSummary>('/reports/summary');
}
