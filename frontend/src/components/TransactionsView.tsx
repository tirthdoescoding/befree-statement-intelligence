import React, { useState, useMemo } from 'react';
import { 
  Search, Filter, ArrowUpDown, Edit3, Check, X, 
  HelpCircle, Sparkles, ChevronLeft, ChevronRight 
} from 'lucide-react';
import { Transaction } from '../types';
import { formatINR, CATEGORY_COLORS } from '../utils';

interface TransactionsViewProps {
  transactions: Transaction[];
  onUpdateCategory: (txnIndex: number, newCategory: string) => void;
  categories: string[];
}

export const TransactionsView: React.FC<TransactionsViewProps> = ({
  transactions,
  onUpdateCategory,
  categories,
}) => {
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [typeFilter, setTypeFilter] = useState<'ALL' | 'DEBIT' | 'CREDIT'>('ALL');
  const [editingId, setEditingId] = useState<number | null>(null);
  const [tempCategory, setTempCategory] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 12;

  const filteredTransactions = useMemo(() => {
    return transactions.filter((t) => {
      const matchesSearch =
        t.description.toLowerCase().includes(search.toLowerCase()) ||
        t.date.includes(search) ||
        (t.category && t.category.toLowerCase().includes(search.toLowerCase()));

      const matchesCat =
        selectedCategory === 'ALL' || t.category === selectedCategory;

      const matchesType =
        typeFilter === 'ALL' ||
        (typeFilter === 'DEBIT' && t.debit && t.debit > 0) ||
        (typeFilter === 'CREDIT' && t.credit && t.credit > 0);

      return matchesSearch && matchesCat && matchesType;
    });
  }, [transactions, search, selectedCategory, typeFilter]);

  const totalPages = Math.ceil(filteredTransactions.length / pageSize) || 1;
  const paginatedTransactions = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredTransactions.slice(start, start + pageSize);
  }, [filteredTransactions, currentPage, pageSize]);

  const handleStartEdit = (idx: number, currentCat: string) => {
    setEditingId(idx);
    setTempCategory(currentCat);
  };

  const handleSaveEdit = (idx: number) => {
    if (tempCategory) {
      onUpdateCategory(idx, tempCategory);
    }
    setEditingId(null);
  };

  return (
    <div className="space-y-6">
      {/* Title & Filter Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-[#17172B] dark:text-white">
            Transactions Registry
          </h2>
          <p className="text-xs text-[#73758A] dark:text-gray-400 mt-1">
            Audited transaction ledger with interactive classification override & confidence tracking
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold px-3 py-1.5 rounded-xl bg-purple-50 dark:bg-purple-950/40 text-[#6C5CE7] border border-purple-200 dark:border-purple-800">
            {filteredTransactions.length} of {transactions.length} entries shown
          </span>
        </div>
      </div>

      {/* Control Filter Bar */}
      <div className="p-4 rounded-2xl bg-white dark:bg-[#161626] border border-[#E9EAF2] dark:border-gray-800 shadow-sm flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="w-4 h-4 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by description, date, or merchant..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setCurrentPage(1);
            }}
            className="w-full pl-9 pr-4 py-2 rounded-xl text-xs bg-[#F7F8FC] dark:bg-[#1A1A2E] border border-[#E9EAF2] dark:border-gray-800 text-[#17172B] dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#6C5CE7]/30"
          />
        </div>

        {/* Category Dropdown */}
        <select
          value={selectedCategory}
          onChange={(e) => {
            setSelectedCategory(e.target.value);
            setCurrentPage(1);
          }}
          className="px-3 py-2 rounded-xl text-xs font-semibold bg-[#F7F8FC] dark:bg-[#1A1A2E] border border-[#E9EAF2] dark:border-gray-800 text-[#17172B] dark:text-white focus:outline-none focus:ring-2 focus:ring-[#6C5CE7]/30"
        >
          <option value="ALL">All Categories</option>
          {categories.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>

        {/* Transaction Flow Filter */}
        <div className="flex items-center rounded-xl bg-[#F7F8FC] dark:bg-[#1A1A2E] p-1 border border-[#E9EAF2] dark:border-gray-800 text-xs font-medium">
          <button
            onClick={() => setTypeFilter('ALL')}
            className={`px-3 py-1 rounded-lg transition-all ${
              typeFilter === 'ALL'
                ? 'bg-white dark:bg-[#161626] text-[#6C5CE7] font-bold shadow-sm'
                : 'text-gray-500 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setTypeFilter('DEBIT')}
            className={`px-3 py-1 rounded-lg transition-all ${
              typeFilter === 'DEBIT'
                ? 'bg-white dark:bg-[#161626] text-rose-500 font-bold shadow-sm'
                : 'text-gray-500 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Debits
          </button>
          <button
            onClick={() => setTypeFilter('CREDIT')}
            className={`px-3 py-1 rounded-lg transition-all ${
              typeFilter === 'CREDIT'
                ? 'bg-white dark:bg-[#161626] text-emerald-500 font-bold shadow-sm'
                : 'text-gray-500 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Credits
          </button>
        </div>
      </div>

      {/* Main Interactive Table */}
      <div className="rounded-3xl bg-white dark:bg-[#161626] border border-[#E9EAF2] dark:border-gray-800 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-[#F7F8FC]/80 dark:bg-[#1A1A2E]/80 border-b border-[#E9EAF2] dark:border-gray-800 text-[#73758A] dark:text-gray-400 font-bold uppercase tracking-wider text-[11px]">
                <th className="py-3.5 px-4">Date</th>
                <th className="py-3.5 px-4 min-w-[240px]">Description & Narration</th>
                <th className="py-3.5 px-4">Category (Editable)</th>
                <th className="py-3.5 px-4">Method & Conf</th>
                <th className="py-3.5 px-4 text-right">Debit (Dr)</th>
                <th className="py-3.5 px-4 text-right">Credit (Cr)</th>
                <th className="py-3.5 px-4 text-right">Running Balance</th>
                <th className="py-3.5 px-4 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E9EAF2] dark:divide-gray-800">
              {paginatedTransactions.map((txn, index) => {
                const actualIndex = (currentPage - 1) * pageSize + index;
                const isEditing = editingId === actualIndex;

                return (
                  <tr
                    key={actualIndex}
                    className="hover:bg-purple-50/20 dark:hover:bg-purple-950/10 transition-colors group"
                  >
                    <td className="py-3 px-4 font-mono text-gray-500 whitespace-nowrap">
                      {txn.date}
                    </td>
                    <td className="py-3 px-4 font-medium text-[#17172B] dark:text-gray-200">
                      {txn.description}
                    </td>

                    {/* Category Cell with inline edit */}
                    <td className="py-3 px-4 whitespace-nowrap">
                      {isEditing ? (
                        <div className="flex items-center gap-1.5">
                          <select
                            value={tempCategory}
                            onChange={(e) => setTempCategory(e.target.value)}
                            className="px-2 py-1 rounded bg-white dark:bg-[#121221] border border-[#6C5CE7] text-xs font-semibold focus:outline-none"
                          >
                            {categories.map((c) => (
                              <option key={c} value={c}>
                                {c}
                              </option>
                            ))}
                          </select>
                          <button
                            onClick={() => handleSaveEdit(actualIndex)}
                            className="p-1 rounded bg-emerald-500 text-white hover:bg-emerald-600"
                          >
                            <Check className="w-3 h-3" />
                          </button>
                          <button
                            onClick={() => setEditingId(null)}
                            className="p-1 rounded bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        </div>
                      ) : (
                        <span
                          className="px-2.5 py-1 rounded-lg font-bold text-[11px] inline-flex items-center gap-1"
                          style={{
                            backgroundColor: `${CATEGORY_COLORS[txn.category] || '#6C5CE7'}18`,
                            color: CATEGORY_COLORS[txn.category] || '#6C5CE7',
                          }}
                        >
                          <span
                            className="w-1.5 h-1.5 rounded-full"
                            style={{ backgroundColor: CATEGORY_COLORS[txn.category] || '#6C5CE7' }}
                          />
                          {txn.category}
                        </span>
                      )}
                    </td>

                    {/* Method & Confidence */}
                    <td className="py-3 px-4 whitespace-nowrap">
                      <div className="flex items-center gap-1.5">
                        <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300">
                          {txn.classification_method || 'rule'}
                        </span>
                        {txn.confidence !== undefined && (
                          <span className="text-[10px] font-mono text-gray-400">
                            {(txn.confidence * 100).toFixed(0)}%
                          </span>
                        )}
                      </div>
                    </td>

                    <td className="py-3 px-4 text-right font-semibold text-rose-500 whitespace-nowrap">
                      {txn.debit ? formatINR(txn.debit) : '—'}
                    </td>
                    <td className="py-3 px-4 text-right font-semibold text-[#12B886] whitespace-nowrap">
                      {txn.credit ? formatINR(txn.credit) : '—'}
                    </td>
                    <td className="py-3 px-4 text-right font-mono font-bold text-[#17172B] dark:text-gray-300 whitespace-nowrap">
                      {txn.balance ? formatINR(txn.balance) : '—'}
                    </td>

                    <td className="py-3 px-4 text-center">
                      {!isEditing && (
                        <button
                          onClick={() => handleStartEdit(actualIndex, txn.category)}
                          title="Edit Category"
                          className="p-1.5 rounded-lg text-gray-400 hover:text-[#6C5CE7] hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                        >
                          <Edit3 className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="p-4 border-t border-[#E9EAF2] dark:border-gray-800 flex items-center justify-between text-xs text-[#73758A]">
          <span>
            Page {currentPage} of {totalPages}
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="p-1.5 rounded-lg border border-gray-200 dark:border-gray-700 disabled:opacity-40 hover:bg-gray-50 dark:hover:bg-gray-800"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="p-1.5 rounded-lg border border-gray-200 dark:border-gray-700 disabled:opacity-40 hover:bg-gray-50 dark:hover:bg-gray-800"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
