import React from 'react';
import { Search, Bell, Sparkles, CheckCircle2 } from 'lucide-react';
import { AccountInfo, Reconciliation } from '../types';

interface TopbarProps {
  accountInfo?: AccountInfo;
  reconciliation?: Reconciliation;
  onOpenUpload: () => void;
}

export const Topbar: React.FC<TopbarProps> = ({
  accountInfo,
  reconciliation,
  onOpenUpload,
}) => {
  return (
    <header className="h-18 px-6 border-b border-[#E9EAF2] dark:border-gray-800 bg-white/80 dark:bg-[#121221]/80 backdrop-blur-md flex items-center justify-between sticky top-0 z-10 transition-colors">
      <div className="flex items-center gap-4 flex-1 max-w-md">
        <div className="relative w-full">
          <Search className="w-4 h-4 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search transactions, accounts, dates..."
            className="w-full pl-10 pr-4 py-2 rounded-xl text-xs sm:text-sm bg-[#F7F8FC] dark:bg-[#1A1A2E] border border-[#E9EAF2] dark:border-gray-800 text-[#17172B] dark:text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#6C5CE7]/30 transition-all"
          />
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Reconciliation Status Badge */}
        {reconciliation && reconciliation.status && (
          <div
            className={`hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border ${
              reconciliation.status === 'ok'
                ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800'
                : 'bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800'
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>
              {reconciliation.status === 'ok' ? 'Audited: Balance Reconciled' : 'Reconciliation Discrepancy'}
            </span>
          </div>
        )}

        {/* Bank & Account Pill */}
        {accountInfo?.bank_name && (
          <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-purple-50 dark:bg-purple-950/30 border border-purple-100 dark:border-purple-900 text-xs font-semibold text-[#6C5CE7]">
            <Sparkles className="w-3.5 h-3.5" />
            <span>{accountInfo.bank_name}</span>
            {accountInfo.account_number && (
              <span className="text-gray-400 font-mono text-[11px]">
                ({accountInfo.account_number.slice(-6)})
              </span>
            )}
          </div>
        )}

        <button
          onClick={onOpenUpload}
          className="px-4 py-2 rounded-xl bg-[#6C5CE7] hover:bg-[#5541C7] text-white text-xs sm:text-sm font-semibold shadow-md shadow-[#6C5CE7]/25 transition-all"
        >
          + Process Statement
        </button>

        <div className="h-6 w-px bg-gray-200 dark:bg-gray-800 mx-1" />

        <button 
          title="Notifications"
          className="w-9 h-9 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 flex items-center justify-center text-[#73758A] transition-colors relative"
        >
          <Bell className="w-4 h-4" />
          <span className="w-2 h-2 rounded-full bg-[#12B886] absolute top-2 right-2 ring-2 ring-white dark:ring-[#121221]" />
        </button>

        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-[#6C5CE7] to-indigo-400 text-white flex items-center justify-center font-bold text-xs shadow-md">
          BF
        </div>
      </div>
    </header>
  );
};
