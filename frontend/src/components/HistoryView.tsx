import React, { useEffect, useState } from 'react';
import { History, FileText, CheckCircle2, ChevronRight, RefreshCw, Calendar, Eye } from 'lucide-react';
import { HistorySession, Transaction } from '../types';
import { formatINR, formatNumber } from '../utils';

interface HistoryViewProps {
  onLoadSessionTransactions: (txns: Transaction[], session: HistorySession) => void;
}

export const HistoryView: React.FC<HistoryViewProps> = ({ onLoadSessionTransactions }) => {
  const [sessions, setSessions] = useState<HistorySession[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/history');
      if (res.ok) {
        const data = await res.json();
        setSessions(data.sessions || []);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleInspect = async (sess: HistorySession) => {
    try {
      const res = await fetch(`/api/history/${sess.id}`);
      if (res.ok) {
        const data = await res.json();
        onLoadSessionTransactions(data.transactions || [], sess);
      }
    } catch (err) {
      alert('Could not retrieve historical transactions.');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[#17172B] dark:text-white">
            Processing History
          </h2>
          <p className="text-xs text-[#73758A] dark:text-gray-400 mt-1">
            Persisted SQLite archive of previously ingested statements and audit logs
          </p>
        </div>
        <button
          onClick={fetchHistory}
          className="p-2.5 rounded-xl border border-gray-200 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800 text-gray-500"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {sessions.length === 0 && !loading ? (
        <div className="p-12 text-center rounded-3xl bg-white dark:bg-[#161626] border border-[#E9EAF2] dark:border-gray-800">
          <History className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <h4 className="text-base font-bold text-[#17172B] dark:text-white">
            No Statements Processed Yet
          </h4>
          <p className="text-xs text-[#73758A] dark:text-gray-400 mt-1">
            Upload and process a PDF statement to create your first session record.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {sessions.map((s) => (
            <div
              key={s.id}
              className="p-5 rounded-2xl bg-white dark:bg-[#161626] border border-[#E9EAF2] dark:border-gray-800 shadow-sm flex flex-wrap items-center justify-between gap-4 hover:border-[#6C5CE7]/40 transition-all"
            >
              <div className="flex items-center gap-3.5">
                <div className="w-10 h-10 rounded-xl bg-[#6C5CE7]/10 text-[#6C5CE7] flex items-center justify-center font-bold">
                  <FileText className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-bold text-[#17172B] dark:text-white">
                      {s.filename}
                    </h4>
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-purple-50 dark:bg-purple-950/40 text-[#6C5CE7]">
                      {s.pdf_type?.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-xs text-[#73758A] dark:text-gray-400 mt-0.5">
                    {s.bank_name || 'Bank Statement'} • {s.account_holder || 'Audited'} •{' '}
                    <span className="font-mono text-gray-400">
                      {new Date(s.processed_at).toLocaleString()}
                    </span>
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-6 text-xs">
                <div>
                  <span className="text-gray-400 block text-[10px] uppercase font-semibold">
                    Volume
                  </span>
                  <span className="font-bold text-[#17172B] dark:text-white">
                    {s.transaction_count} txns
                  </span>
                </div>

                <div>
                  <span className="text-gray-400 block text-[10px] uppercase font-semibold">
                    Total Credits
                  </span>
                  <span className="font-bold text-[#12B886]">
                    {formatINR(s.total_credits)}
                  </span>
                </div>

                <div>
                  <span className="text-gray-400 block text-[10px] uppercase font-semibold">
                    Total Debits
                  </span>
                  <span className="font-bold text-rose-500">
                    {formatINR(s.total_debits)}
                  </span>
                </div>

                <button
                  onClick={() => handleInspect(s)}
                  className="px-3.5 py-2 rounded-xl bg-[#F7F8FC] dark:bg-[#1A1A2E] hover:bg-[#6C5CE7] hover:text-white text-[#17172B] dark:text-white font-semibold transition-all flex items-center gap-1.5 text-xs"
                >
                  <Eye className="w-3.5 h-3.5" /> Inspect Ledger
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
