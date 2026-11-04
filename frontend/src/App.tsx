import React, { useState, useEffect } from 'react';
import { LandingPage } from './components/LandingPage';
import { Sidebar } from './components/Sidebar';
import { Topbar } from './components/Topbar';
import { OverviewDashboard } from './components/OverviewDashboard';
import { UploadModal } from './components/UploadModal';
import { TransactionsView } from './components/TransactionsView';
import { ExportCenter } from './components/ExportCenter';
import { HistoryView } from './components/HistoryView';
import { SettingsView } from './components/SettingsView';
import { ProcessResponse, Transaction, HistorySession } from './types';

// Mock initial data so users see a populated dashboard upon landing if they wish
const DEMO_RESPONSE: ProcessResponse = {
  success: true,
  session_id: 1,
  filename: 'sbi_statement_jan2024.pdf',
  pdf_type: 'text',
  pages: 1,
  account_info: {
    account_holder: 'Rajesh Kumar Sharma',
    account_number: 'XXXX1234',
    ifsc_code: 'SBIN0001234',
    bank_name: 'State Bank of India',
    statement_period: '01/01/2024 to 31/01/2024',
    opening_balance: 50000,
    closing_balance: 68951,
  },
  reconciliation: {
    opening_balance: 50000,
    closing_balance: 68951,
    total_debits: 71099,
    total_credits: 90050,
    calculated_closing: 68951,
    difference: 0,
    status: 'ok',
    message: 'Audit Verified: Opening + Credits - Debits exactly matches Closing Balance.',
  },
  transactions: [
    { date: '2024-01-01', description: 'SALARY CREDIT JAN 2024', debit: null, credit: 75000, balance: 125000, category: 'Salary', confidence: 0.95, classification_method: 'rule' },
    { date: '2024-01-02', description: 'UPI/SWIGGY/FOOD ORDER', debit: 450, credit: null, balance: 124550, category: 'Food & Dining', confidence: 0.95, classification_method: 'rule' },
    { date: '2024-01-03', description: 'NEFT/RENT PAYMENT/LANDLORD', debit: 15000, credit: null, balance: 109550, category: 'Rent', confidence: 0.95, classification_method: 'rule' },
    { date: '2024-01-04', description: 'ATM CASH WITHDRAWAL', debit: 10000, credit: null, balance: 99550, category: 'ATM Withdrawal', confidence: 0.95, classification_method: 'rule' },
    { date: '2024-01-05', description: 'AMAZON SHOPPING PURCHASE', debit: 2500, credit: null, balance: 97050, category: 'Shopping', confidence: 0.95, classification_method: 'rule' },
    { date: '2024-01-06', description: 'AIRTEL BILL PAYMENT', debit: 599, credit: null, balance: 96451, category: 'Utilities', confidence: 0.95, classification_method: 'rule' },
    { date: '2024-01-07', description: 'HDFC LIFE INSURANCE PREMIUM', debit: 5000, credit: null, balance: 91451, category: 'Insurance', confidence: 0.95, classification_method: 'rule' },
    { date: '2024-01-08', description: 'SIP HDFC MF JAN 2024', debit: 2000, credit: null, balance: 89451, category: 'Investment', confidence: 0.95, classification_method: 'rule' },
    { date: '2024-01-09', description: 'INTEREST CREDIT', debit: null, credit: 250, balance: 89701, category: 'Interest', confidence: 0.95, classification_method: 'rule' },
    { date: '2024-01-10', description: 'EMI HOME LOAN PAYMENT', debit: 25000, credit: null, balance: 64701, category: 'EMI / Loan', confidence: 0.95, classification_method: 'rule' },
    { date: '2024-01-11', description: 'UBER RIDE PAYMENT', debit: 350, credit: null, balance: 64351, category: 'Transportation', confidence: 0.95, classification_method: 'rule' },
    { date: '2024-01-12', description: 'CONSULTING FEE CREDIT', debit: null, credit: 15000, balance: 79351, category: 'Business Transactions', confidence: 0.95, classification_method: 'rule' },
    { date: '2024-01-13', description: 'ELECTRICITY BILL BESCOM', debit: 1200, credit: null, balance: 78151, category: 'Utilities', confidence: 0.95, classification_method: 'rule' },
    { date: '2024-01-14', description: 'SCHOOL FEE PAYMENT', debit: 8000, credit: null, balance: 70151, category: 'Education', confidence: 0.95, classification_method: 'rule' },
    { date: '2024-01-15', description: 'IRCTC TRAIN TICKET', debit: 1200, credit: null, balance: 68951, category: 'Transportation', confidence: 0.95, classification_method: 'rule' },
  ],
  analytics: {
    total_transactions: 15,
    total_debit: 71099,
    total_credit: 90050,
    net_flow: 18951,
    category_breakdown: [
      { category: 'Salary', count: 1, debit: 0, credit: 75000 },
      { category: 'Food & Dining', count: 1, debit: 450, credit: 0 },
      { category: 'Rent', count: 1, debit: 15000, credit: 0 },
      { category: 'ATM Withdrawal', count: 1, debit: 10000, credit: 0 },
      { category: 'Shopping', count: 1, debit: 2500, credit: 0 },
      { category: 'Utilities', count: 2, debit: 1799, credit: 0 },
      { category: 'Insurance', count: 1, debit: 5000, credit: 0 },
      { category: 'Investment', count: 1, debit: 2000, credit: 0 },
      { category: 'Interest', count: 1, debit: 0, credit: 250 },
      { category: 'EMI / Loan', count: 1, debit: 25000, credit: 0 },
      { category: 'Transportation', count: 2, debit: 1550, credit: 0 },
      { category: 'Business Transactions', count: 1, debit: 0, credit: 15000 },
      { category: 'Education', count: 1, debit: 8000, credit: 0 },
    ],
    monthly_trends: [
      { month: 'Jan 2024', debit: 71099, credit: 90050, count: 15 },
    ],
  },
};

export function App() {
  const [view, setView] = useState<'landing' | 'app'>('landing');
  const [activeTab, setActiveTab] = useState('overview');
  const [collapsed, setCollapsed] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [statementData, setStatementData] = useState<ProcessResponse>(DEMO_RESPONSE);
  const [categories, setCategories] = useState<string[]>([
    'Salary',
    'Food & Dining',
    'Shopping',
    'Rent',
    'Utilities',
    'Healthcare',
    'Transportation',
    'ATM Withdrawal',
    'Bank Charges',
    'EMI / Loan',
    'Investment',
    'Insurance',
    'Education',
    'Transfers',
    'Business Transactions',
    'Interest',
    'Other / Uncategorized',
  ]);

  useEffect(() => {
    fetch('/api/categories')
      .then((r) => r.json())
      .then((data) => {
        if (data.categories) setCategories(data.categories);
      })
      .catch(() => {});
  }, []);

  const handleProcessComplete = (data: ProcessResponse) => {
    setStatementData(data);
    setActiveTab('overview');
  };

  const handleUpdateCategory = (txnIdx: number, newCategory: string) => {
    setStatementData((prev) => {
      const updatedTxns = [...prev.transactions];
      if (updatedTxns[txnIdx]) {
        updatedTxns[txnIdx] = {
          ...updatedTxns[txnIdx],
          category: newCategory,
          classification_method: 'manual',
          confidence: 1.0,
        };
      }
      return {
        ...prev,
        transactions: updatedTxns,
      };
    });
  };

  const handleLoadSessionTransactions = (txns: Transaction[], session: HistorySession) => {
    setStatementData({
      success: true,
      session_id: session.id,
      filename: session.filename,
      pdf_type: session.pdf_type,
      pages: session.pages,
      account_info: {
        account_holder: session.account_holder,
        account_number: session.account_number,
        bank_name: session.bank_name,
        opening_balance: session.opening_balance,
        closing_balance: session.closing_balance,
      },
      transactions: txns,
      analytics: {
        total_transactions: session.transaction_count,
        total_debit: session.total_debits || 0,
        total_credit: session.total_credits || 0,
        net_flow: (session.total_credits || 0) - (session.total_debits || 0),
        category_breakdown: [],
        monthly_trends: [],
      },
    });
    setActiveTab('overview');
  };

  return (
    <div className={darkMode ? 'dark' : ''}>
      {view === 'landing' ? (
        <LandingPage
          onStart={() => {
            setView('app');
            setActiveTab('upload');
          }}
          onExplore={() => {
            setView('app');
            setActiveTab('overview');
          }}
        />
      ) : (
        <div className="flex h-screen overflow-hidden bg-[#F7F8FC] dark:bg-[#0B0B14] transition-colors">
          <Sidebar
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            collapsed={collapsed}
            setCollapsed={setCollapsed}
            darkMode={darkMode}
            setDarkMode={setDarkMode}
            onReturnHome={() => setView('landing')}
          />

          <div className="flex-1 flex flex-col overflow-y-auto">
            <Topbar
              accountInfo={statementData.account_info}
              reconciliation={statementData.reconciliation}
              onOpenUpload={() => setActiveTab('upload')}
            />

            <main className="p-6 md:p-8 max-w-7xl mx-auto w-full flex-1">
              {activeTab === 'overview' && (
                <OverviewDashboard
                  data={statementData}
                  onNavigateTab={(tab) => setActiveTab(tab)}
                />
              )}

              {activeTab === 'upload' && (
                <UploadModal
                  onProcessComplete={handleProcessComplete}
                  onCancel={() => setActiveTab('overview')}
                />
              )}

              {activeTab === 'transactions' && (
                <TransactionsView
                  transactions={statementData.transactions}
                  onUpdateCategory={handleUpdateCategory}
                  categories={categories}
                />
              )}

              {activeTab === 'analytics' && (
                <OverviewDashboard
                  data={statementData}
                  onNavigateTab={(tab) => setActiveTab(tab)}
                />
              )}

              {activeTab === 'export' && (
                <ExportCenter data={statementData} />
              )}

              {activeTab === 'history' && (
                <HistoryView
                  onLoadSessionTransactions={handleLoadSessionTransactions}
                />
              )}

              {activeTab === 'settings' && (
                <SettingsView categories={categories} />
              )}
            </main>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
