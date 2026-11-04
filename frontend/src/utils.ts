import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatINR(val?: number | null): string {
  if (val === null || val === undefined || isNaN(val)) return '₹0.00';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2,
  }).format(val);
}

export function formatNumber(val?: number | null): string {
  if (val === null || val === undefined || isNaN(val)) return '0';
  return new Intl.NumberFormat('en-IN').format(val);
}

export const CATEGORY_COLORS: Record<string, string> = {
  'Salary': '#12B886',
  'Food & Dining': '#F59E0B',
  'Shopping': '#EC4899',
  'Rent': '#F43F5E',
  'Utilities': '#3B82F6',
  'Healthcare': '#EF4444',
  'Transportation': '#8B5CF6',
  'ATM Withdrawal': '#6366F1',
  'Bank Charges': '#94A3B8',
  'EMI / Loan': '#D97706',
  'Investment': '#10B981',
  'Insurance': '#06B6D4',
  'Education': '#14B8A6',
  'Transfers': '#6C5CE7',
  'Business Transactions': '#64748B',
  'Interest': '#84CC16',
  'Other / Uncategorized': '#A1A1AA',
};
