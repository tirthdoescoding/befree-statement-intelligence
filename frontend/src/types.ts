export interface Transaction {
  id?: number;
  date: string;
  description: string;
  debit: number | null;
  credit: number | null;
  balance: number | null;
  category: string;
  confidence?: number;
  classification_method?: string;
  month?: string;
}

export interface AccountInfo {
  account_holder?: string;
  account_number?: string;
  ifsc_code?: string;
  bank_name?: string;
  statement_period?: string;
  opening_balance?: string | number;
  closing_balance?: string | number;
}

export interface Reconciliation {
  opening_balance?: number | null;
  closing_balance?: number | null;
  total_debits?: number;
  total_credits?: number;
  calculated_closing?: number | null;
  difference?: number | null;
  status?: 'ok' | 'warning' | 'unknown';
  message?: string;
}

export interface CategoryBreakdown {
  category: string;
  count: number;
  debit: number;
  credit: number;
}

export interface MonthlyTrend {
  month: string;
  debit: number;
  credit: number;
  count: number;
}

export interface ProcessResponse {
  success: boolean;
  message?: string;
  session_id?: number;
  filename?: string;
  pdf_type?: string;
  pages?: number;
  account_info?: AccountInfo;
  reconciliation?: Reconciliation;
  warnings?: string[];
  transactions: Transaction[];
  analytics?: {
    total_transactions: number;
    total_debit: number;
    total_credit: number;
    net_flow: number;
    category_breakdown: CategoryBreakdown[];
    monthly_trends: MonthlyTrend[];
  };
}

export interface HistorySession {
  id: number;
  filename: string;
  processed_at: string;
  pdf_type: string;
  pages: number;
  transaction_count: number;
  account_holder?: string;
  account_number?: string;
  bank_name?: string;
  opening_balance?: number;
  closing_balance?: number;
  total_debits?: number;
  total_credits?: number;
  reconciliation_status?: string;
  warnings?: string;
}
