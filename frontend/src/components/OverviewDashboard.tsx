import React from 'react';
import { 
  ArrowUpRight, ArrowDownRight, TrendingUp, ReceiptText, 
  Wallet, ShieldCheck, AlertTriangle, ArrowRight, Building2, Calendar
} from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, PieChart, Pie, Cell } from 'recharts';
import { ProcessResponse } from '../types';
import { formatINR, formatNumber, CATEGORY_COLORS } from '../utils';

interface OverviewProps {
  data: ProcessResponse;
  onNavigateTab: (tab: string) => void;
}

export const OverviewDashboard: React.FC<OverviewProps> = ({ data, onNavigateTab }) => {
  const analytics = data.analytics;
  const recon = data.reconciliation;
  const account = data.account_info;

  const totalTransactions = analytics?.total_transactions || data.transactions.length || 0;
  const totalDebit = analytics?.total_debit || 0;
  const totalCredit = analytics?.total_credit || 0;
  const netFlow = analytics?.net_flow || (totalCredit - totalDebit);

  // Category breakdown data
  const pieData = analytics?.category_breakdown
    ? analytics.category_breakdown.map((item) => ({
        name: item.category,
        value: item.count,
        amount: item.debit + item.credit,
      }))
    : [];

  const trendData = analytics?.monthly_trends || [];

  return (
    <div className="space-y-6">
      {/* Account Info Banner */}
      {account && account.bank_name && (
        <div className="p-6 rounded-3xl bg-gradient-to-r from-[#17172B] via-[#1E1E38] to-[#2B2B4A] text-white flex flex-wrap items-center justify-between gap-4 shadow-xl">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-[#6C5CE7] flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-[#6C5CE7]/30">
              <Building2 className="w-7 h-7" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold">{account.bank_name}</span>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-white/10 text-white/90">
                  {data.pdf_type?.toUpperCase()} PDF
                </span>
              </div>
              <p className="text-xs text-gray-300 mt-1">
                Holder: <strong className="text-white">{account.account_holder || 'Valued Customer'}</strong> • 
                A/C: <span className="font-mono text-purple-200">{account.account_number || 'N/A'}</span> • 
                IFSC: <span className="font-mono">{account.ifsc_code || 'N/A'}</span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-6 text-xs">
            {account.statement_period && (
              <div className="flex items-center gap-2 text-gray-300">
                <Calendar className="w-4 h-4 text-purple-400" />
                <span>{account.statement_period}</span>
              </div>
            )}
            <button
              onClick={() => onNavigateTab('export')}
              className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-white font-semibold transition-all flex items-center gap-2"
            >
              Export Sheets <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Transactions */}
        <div className="p-5 rounded-2xl bg-white dark:bg-[#161626] border border-[#E9EAF2] dark:border-gray-800 shadow-sm hover:shadow-md transition-all">
          <div className="flex items-center justify-between text-[#73758A] dark:text-gray-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Transactions</span>
            <div className="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-950/40 text-[#6C5CE7] flex items-center justify-center">
              <ReceiptText className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-[#17172B] dark:text-white">
            {formatNumber(totalTransactions)}
          </div>
          <span className="text-[11px] text-[#12B886] font-semibold flex items-center gap-1 mt-1">
            <TrendingUp className="w-3 h-3" /> Extracted & Normalized
          </span>
        </div>

        {/* Total Credits */}
        <div className="p-5 rounded-2xl bg-white dark:bg-[#161626] border border-[#E9EAF2] dark:border-gray-800 shadow-sm hover:shadow-md transition-all">
          <div className="flex items-center justify-between text-[#73758A] dark:text-gray-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Inflow (Credits)</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 text-[#12B886] flex items-center justify-center">
              <ArrowDownRight className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-[#12B886]">
            {formatINR(totalCredit)}
          </div>
          <span className="text-[11px] text-gray-400 font-medium mt-1 inline-block">
            Income, transfers & interest
          </span>
        </div>

        {/* Total Debits */}
        <div className="p-5 rounded-2xl bg-white dark:bg-[#161626] border border-[#E9EAF2] dark:border-gray-800 shadow-sm hover:shadow-md transition-all">
          <div className="flex items-center justify-between text-[#73758A] dark:text-gray-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Outflow (Debits)</span>
            <div className="w-8 h-8 rounded-lg bg-rose-50 dark:bg-rose-950/40 text-rose-500 flex items-center justify-center">
              <ArrowUpRight className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-rose-500">
            {formatINR(totalDebit)}
          </div>
          <span className="text-[11px] text-gray-400 font-medium mt-1 inline-block">
            Expenses, withdrawals & EMIs
          </span>
        </div>

        {/* Net Cash Flow */}
        <div className="p-5 rounded-2xl bg-white dark:bg-[#161626] border border-[#E9EAF2] dark:border-gray-800 shadow-sm hover:shadow-md transition-all">
          <div className="flex items-center justify-between text-[#73758A] dark:text-gray-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Net Cash Flow</span>
            <div className="w-8 h-8 rounded-lg bg-purple-50 dark:bg-purple-950/40 text-[#6C5CE7] flex items-center justify-center">
              <Wallet className="w-4 h-4" />
            </div>
          </div>
          <div className={`text-2xl font-black ${netFlow >= 0 ? 'text-[#12B886]' : 'text-rose-500'}`}>
            {formatINR(netFlow)}
          </div>
          <span className="text-[11px] text-gray-400 font-medium mt-1 inline-block">
            Credits minus Debits
          </span>
        </div>
      </div>

      {/* Balance Reconciliation Audit Banner */}
      {recon && (
        <div
          className={`p-5 rounded-2xl border flex flex-wrap items-center justify-between gap-4 transition-colors ${
            recon.status === 'ok'
              ? 'bg-emerald-50/70 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-800/60 text-emerald-900 dark:text-emerald-300'
              : 'bg-amber-50/70 dark:bg-amber-950/20 border-amber-200 dark:border-amber-800/60 text-amber-900 dark:text-amber-300'
          }`}
        >
          <div className="flex items-center gap-3">
            <div
              className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                recon.status === 'ok' ? 'bg-emerald-600 text-white' : 'bg-amber-500 text-white'
              }`}
            >
              {recon.status === 'ok' ? <ShieldCheck className="w-6 h-6" /> : <AlertTriangle className="w-6 h-6" />}
            </div>
            <div>
              <h4 className="text-sm font-bold">
                {recon.status === 'ok'
                  ? 'Audit Passed: Mathematical Reconciliation Verified'
                  : 'Reconciliation Audit Notice'}
              </h4>
              <p className="text-xs opacity-90 mt-0.5">{recon.message}</p>
            </div>
          </div>

          <div className="flex items-center gap-4 text-xs font-mono">
            <div>
              <span className="opacity-70">Opening:</span>{' '}
              <strong>{formatINR(recon.opening_balance)}</strong>
            </div>
            <div>
              <span className="opacity-70">Calculated Closing:</span>{' '}
              <strong>{formatINR(recon.calculated_closing)}</strong>
            </div>
            <div>
              <span className="opacity-70">Reported Closing:</span>{' '}
              <strong>{formatINR(recon.closing_balance)}</strong>
            </div>
          </div>
        </div>
      )}

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Debit vs Credit Inflow/Outflow */}
        <div className="lg:col-span-2 p-6 rounded-3xl bg-white dark:bg-[#161626] border border-[#E9EAF2] dark:border-gray-800 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-[#17172B] dark:text-white">
                Monthly Inflow & Outflow Trends
              </h3>
              <p className="text-xs text-[#73758A] dark:text-gray-400">
                Visualizing debits vs credits extracted from the statements
              </p>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <span className="flex items-center gap-1.5 font-medium text-emerald-600">
                <span className="w-2.5 h-2.5 rounded-full bg-[#12B886]" /> Credits
              </span>
              <span className="flex items-center gap-1.5 font-medium text-rose-500">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-400" /> Debits
              </span>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={trendData.length > 0 ? trendData : [{ month: 'Current', debit: totalDebit, credit: totalCredit, count: 1 }]}>
                <XAxis dataKey="month" stroke="#94A3B8" fontSize={12} tickLine={false} />
                <YAxis stroke="#94A3B8" fontSize={12} tickLine={false} tickFormatter={(val) => `₹${val / 1000}k`} />
                <Tooltip
                  formatter={(value: any) => [formatINR(Number(value)), '']}
                  contentStyle={{ backgroundColor: '#17172B', borderColor: '#2D2D4A', borderRadius: '12px', color: '#fff', fontSize: '12px' }}
                />
                <Bar dataKey="credit" fill="#12B886" radius={[6, 6, 0, 0]} />
                <Bar dataKey="debit" fill="#F87171" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category Breakdown Donut */}
        <div className="p-6 rounded-3xl bg-white dark:bg-[#161626] border border-[#E9EAF2] dark:border-gray-800 shadow-sm flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-[#17172B] dark:text-white mb-1">
              Category Distribution
            </h3>
            <p className="text-xs text-[#73758A] dark:text-gray-400 mb-4">
              Classified by Heuristic & LinearSVC ML
            </p>

            <div className="h-52 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    innerRadius={55}
                    outerRadius={80}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={CATEGORY_COLORS[entry.name] || '#6C5CE7'} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(val: any, name: any) => [`${val} transactions`, name]}
                    contentStyle={{ backgroundColor: '#17172B', borderColor: '#2D2D4A', borderRadius: '12px', color: '#fff', fontSize: '12px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="space-y-1.5 mt-2 max-h-32 overflow-y-auto pr-1 text-xs">
            {pieData.slice(0, 5).map((cat, i) => (
              <div key={i} className="flex items-center justify-between py-1 border-b border-gray-100 dark:border-gray-800/60">
                <span className="flex items-center gap-2 text-[#73758A] dark:text-gray-300">
                  <span
                    className="w-2.5 h-2.5 rounded-full"
                    style={{ backgroundColor: CATEGORY_COLORS[cat.name] || '#6C5CE7' }}
                  />
                  {cat.name}
                </span>
                <span className="font-semibold text-[#17172B] dark:text-white">
                  {cat.value} txn
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick View Latest Transactions Table */}
      <div className="p-6 rounded-3xl bg-white dark:bg-[#161626] border border-[#E9EAF2] dark:border-gray-800 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-bold text-[#17172B] dark:text-white">
              Recent Transactions
            </h3>
            <p className="text-xs text-[#73758A] dark:text-gray-400">
              Extracted entries preview (Click to view full interactive table)
            </p>
          </div>
          <button
            onClick={() => onNavigateTab('transactions')}
            className="text-xs font-semibold text-[#6C5CE7] hover:text-[#5541C7] flex items-center gap-1"
          >
            View all {totalTransactions} transactions <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-[#E9EAF2] dark:border-gray-800 text-[#73758A] font-semibold">
                <th className="py-2.5 px-3">Date</th>
                <th className="py-2.5 px-3">Description</th>
                <th className="py-2.5 px-3">Category</th>
                <th className="py-2.5 px-3 text-right">Debit</th>
                <th className="py-2.5 px-3 text-right">Credit</th>
                <th className="py-2.5 px-3 text-right">Balance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E9EAF2] dark:divide-gray-800">
              {data.transactions.slice(0, 6).map((txn, idx) => (
                <tr key={idx} className="hover:bg-gray-50/60 dark:hover:bg-gray-800/30 transition-colors">
                  <td className="py-3 px-3 font-mono text-gray-500 whitespace-nowrap">{txn.date}</td>
                  <td className="py-3 px-3 font-medium text-[#17172B] dark:text-gray-200 max-w-xs truncate">
                    {txn.description}
                  </td>
                  <td className="py-3 px-3">
                    <span
                      className="px-2 py-0.5 rounded-md font-semibold text-[11px]"
                      style={{
                        backgroundColor: `${CATEGORY_COLORS[txn.category] || '#6C5CE7'}18`,
                        color: CATEGORY_COLORS[txn.category] || '#6C5CE7',
                      }}
                    >
                      {txn.category}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-right font-semibold text-rose-500 whitespace-nowrap">
                    {txn.debit ? formatINR(txn.debit) : '—'}
                  </td>
                  <td className="py-3 px-3 text-right font-semibold text-[#12B886] whitespace-nowrap">
                    {txn.credit ? formatINR(txn.credit) : '—'}
                  </td>
                  <td className="py-3 px-3 text-right font-mono font-medium text-[#17172B] dark:text-gray-300 whitespace-nowrap">
                    {txn.balance ? formatINR(txn.balance) : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
