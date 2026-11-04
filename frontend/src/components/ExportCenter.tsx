import React, { useState } from 'react';
import { 
  FileSpreadsheet, FileText, Download, CheckCircle2, 
  Sparkles, Layers, ShieldCheck, Database 
} from 'lucide-react';
import { ProcessResponse } from '../types';
import { formatNumber } from '../utils';

interface ExportCenterProps {
  data: ProcessResponse;
}

export const ExportCenter: React.FC<ExportCenterProps> = ({ data }) => {
  const [downloadingExcel, setDownloadingExcel] = useState(false);
  const [downloadingCsv, setDownloadingCsv] = useState(false);
  const [successNotice, setSuccessNotice] = useState<string | null>(null);

  const totalTxns = data.transactions.length;

  const triggerDownload = (blob: Blob, filename: string) => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const handleExportExcel = async () => {
    setDownloadingExcel(true);
    setSuccessNotice(null);
    try {
      const res = await fetch('/api/export/excel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          transactions: data.transactions,
          account_info: data.account_info || {},
          reconciliation: data.reconciliation || {},
        }),
      });
      if (!res.ok) throw new Error('Excel generation failed');
      const blob = await res.blob();
      triggerDownload(blob, `bank_statement_${Date.now()}.xlsx`);
      setSuccessNotice('Excel workbook downloaded successfully with all 3 formatted worksheets.');
    } catch (err: any) {
      alert(err.message || 'Export error');
    } finally {
      setDownloadingExcel(false);
    }
  };

  const handleExportCsv = async () => {
    setDownloadingCsv(true);
    setSuccessNotice(null);
    try {
      const res = await fetch('/api/export/csv', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          transactions: data.transactions,
          account_info: data.account_info || {},
          reconciliation: data.reconciliation || {},
        }),
      });
      if (!res.ok) throw new Error('CSV generation failed');
      const blob = await res.blob();
      triggerDownload(blob, `bank_statement_${Date.now()}.csv`);
      setSuccessNotice('Clean UTF-8 CSV downloaded successfully.');
    } catch (err: any) {
      alert(err.message || 'Export error');
    } finally {
      setDownloadingCsv(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-[#17172B] dark:text-white">
          Export Center
        </h2>
        <p className="text-xs text-[#73758A] dark:text-gray-400 mt-1">
          Generate executive-level multi-sheet spreadsheets and clean tabular datasets
        </p>
      </div>

      {successNotice && (
        <div className="p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-xs font-semibold text-emerald-800 dark:text-emerald-300 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-500" />
          <span>{successNotice}</span>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Excel Card */}
        <div className="p-7 rounded-3xl bg-white dark:bg-[#161626] border border-[#E9EAF2] dark:border-gray-800 shadow-sm flex flex-col justify-between">
          <div>
            <div className="w-12 h-12 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 flex items-center justify-center mb-4">
              <FileSpreadsheet className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-[#17172B] dark:text-white mb-2">
              Executive Excel (.xlsx)
            </h3>
            <p className="text-xs text-[#73758A] dark:text-gray-400 leading-relaxed mb-6">
              Complete 3-worksheet financial model with automatic styling, freeze panes, debit/credit tinting, and reconciliation audit sections.
            </p>

            <div className="space-y-2 mb-8 text-xs font-medium text-[#17172B] dark:text-gray-300">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-emerald-500" />
                <span>Sheet 1: Account & Reconciliation Summary</span>
              </div>
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-emerald-500" />
                <span>Sheet 2: Formatted & Filtered Transactions</span>
              </div>
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-emerald-500" />
                <span>Sheet 3: Category Volume & Count Breakdown</span>
              </div>
            </div>
          </div>

          <button
            onClick={handleExportExcel}
            disabled={downloadingExcel || totalTxns === 0}
            className="w-full py-3.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white text-xs sm:text-sm font-semibold shadow-lg shadow-emerald-600/25 transition-all flex items-center justify-center gap-2"
          >
            <Download className="w-4 h-4" />
            {downloadingExcel ? 'Generating Workbook...' : `Export Excel (${formatNumber(totalTxns)} rows)`}
          </button>
        </div>

        {/* CSV Card */}
        <div className="p-7 rounded-3xl bg-white dark:bg-[#161626] border border-[#E9EAF2] dark:border-gray-800 shadow-sm flex flex-col justify-between">
          <div>
            <div className="w-12 h-12 rounded-2xl bg-blue-50 dark:bg-blue-950/40 text-blue-600 flex items-center justify-center mb-4">
              <FileText className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-[#17172B] dark:text-white mb-2">
              Tabular CSV (.csv)
            </h3>
            <p className="text-xs text-[#73758A] dark:text-gray-400 leading-relaxed mb-6">
              Standardized UTF-8 flat file with classified category labels, confidence scores, and clean currency numeric values.
            </p>

            <div className="space-y-2 mb-8 text-xs font-medium text-[#17172B] dark:text-gray-300">
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4 text-blue-500" />
                <span>100% Compatible with QuickBooks, Tally, Zoho</span>
              </div>
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4 text-blue-500" />
                <span>Clean comma-separated columns</span>
              </div>
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4 text-blue-500" />
                <span>Includes ML classification method tag</span>
              </div>
            </div>
          </div>

          <button
            onClick={handleExportCsv}
            disabled={downloadingCsv || totalTxns === 0}
            className="w-full py-3.5 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-xs sm:text-sm font-semibold shadow-lg shadow-blue-600/25 transition-all flex items-center justify-center gap-2"
          >
            <Download className="w-4 h-4" />
            {downloadingCsv ? 'Generating CSV...' : `Export CSV (${formatNumber(totalTxns)} rows)`}
          </button>
        </div>
      </div>
    </div>
  );
};
