import React from 'react';
import { motion } from 'framer-motion';
import { 
  ArrowRight, ShieldCheck, Zap, FileSpreadsheet, Sparkles, 
  ChevronRight, CheckCircle2, TrendingUp, Cpu
} from 'lucide-react';

interface LandingProps {
  onStart: () => void;
  onExplore: () => void;
}

export const LandingPage: React.FC<LandingProps> = ({ onStart, onExplore }) => {
  return (
    <div className="relative min-h-screen bg-[#F7F8FC] dark:bg-[#0B0B14] overflow-hidden transition-colors">
      {/* Background Glow Mesh */}
      <div className="absolute top-[-20%] left-[-10%] w-[650px] h-[650px] rounded-full bg-gradient-to-br from-[#6C5CE7]/20 to-purple-400/10 blur-[130px] pointer-events-none" />
      <div className="absolute top-[20%] right-[-15%] w-[600px] h-[600px] rounded-full bg-gradient-to-bl from-teal-400/15 to-indigo-500/10 blur-[120px] pointer-events-none" />

      {/* Navigation Header */}
      <header className="relative z-10 max-w-7xl mx-auto px-6 py-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#6C5CE7] to-indigo-400 flex items-center justify-center text-white font-bold shadow-lg shadow-[#6C5CE7]/30">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="font-extrabold text-xl tracking-tight text-[#17172B] dark:text-white">
              Befree <span className="text-[#6C5CE7]">Intelligence</span>
            </span>
            <span className="hidden sm:inline-block ml-2 text-xs font-semibold px-2 py-0.5 rounded-full bg-[#6C5CE7]/10 text-[#6C5CE7] border border-[#6C5CE7]/20">
              v2.0 Non-LLM
            </span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <button 
            onClick={onExplore}
            className="text-sm font-semibold text-[#73758A] dark:text-gray-300 hover:text-[#6C5CE7] transition-colors"
          >
            Dashboard Demo
          </button>
          <button
            onClick={onStart}
            className="px-5 py-2.5 rounded-xl bg-[#6C5CE7] hover:bg-[#5541C7] text-white text-sm font-medium shadow-md shadow-[#6C5CE7]/25 transition-all flex items-center gap-2 hover:scale-[1.02]"
          >
            Launch Processor <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative z-10 max-w-6xl mx-auto px-6 pt-16 pb-24 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white dark:bg-[#161626] border border-[#E9EAF2] dark:border-gray-800 shadow-sm mb-6"
        >
          <Sparkles className="w-4 h-4 text-[#6C5CE7]" />
          <span className="text-xs font-semibold text-[#17172B] dark:text-gray-200">
            Next-Gen Automated Financial Ingestion Platform
          </span>
          <ChevronRight className="w-3.5 h-3.5 text-gray-400" />
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-[#17172B] dark:text-white leading-[1.12]"
        >
          Your Bank Statements.<br />
          <span className="bg-gradient-to-r from-[#6C5CE7] via-indigo-500 to-teal-400 bg-clip-text text-transparent">
            Organized Intelligently.
          </span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-6 max-w-2xl mx-auto text-base sm:text-lg text-[#73758A] dark:text-gray-300 leading-relaxed font-normal"
        >
          Extract, classify, and analyze financial transactions from bank statements with a powerful automated processing platform. Built with hybrid heuristics and supervised machine learning — zero external LLM dependencies.
        </motion.p>

        {/* Hero Actions */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-10 flex flex-wrap items-center justify-center gap-4"
        >
          <button
            onClick={onStart}
            className="px-8 py-4 rounded-xl bg-[#6C5CE7] hover:bg-[#5541C7] text-white font-semibold text-base shadow-xl shadow-[#6C5CE7]/30 transition-all flex items-center gap-3 hover:-translate-y-0.5 active:translate-y-0"
          >
            Process Statement <ArrowRight className="w-5 h-5" />
          </button>
          <button
            onClick={onExplore}
            className="px-8 py-4 rounded-xl bg-white dark:bg-[#161626] hover:bg-gray-50 dark:hover:bg-[#1f1f33] text-[#17172B] dark:text-white font-semibold text-base border border-[#E9EAF2] dark:border-gray-800 shadow-sm transition-all hover:-translate-y-0.5"
          >
            Explore Dashboard
          </button>
        </motion.div>

        {/* Feature Badges */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="mt-14 flex flex-wrap justify-center items-center gap-6 text-xs text-[#73758A] dark:text-gray-400 font-medium"
        >
          <div className="flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-[#12B886]" /> Text & Scanned PDF OCR
          </div>
          <div className="flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-[#12B886]" /> 17 Financial Categories
          </div>
          <div className="flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-[#12B886]" /> Balance Reconciliation
          </div>
          <div className="flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-[#12B886]" /> Instant Multi-sheet Excel
          </div>
        </motion.div>

        {/* Floating Preview Card Mockup */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.45 }}
          className="mt-16 relative mx-auto max-w-4xl rounded-2xl p-2 bg-gradient-to-b from-white/80 to-white/20 dark:from-white/10 dark:to-transparent border border-white/60 dark:border-white/10 shadow-2xl backdrop-blur-xl"
        >
          <div className="rounded-xl overflow-hidden bg-white dark:bg-[#161626] border border-[#E9EAF2] dark:border-gray-800 p-6 text-left">
            <div className="flex items-center justify-between border-b border-[#E9EAF2] dark:border-gray-800 pb-4 mb-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-400" />
                <div className="w-3 h-3 rounded-full bg-yellow-400" />
                <div className="w-3 h-3 rounded-full bg-green-400" />
                <span className="ml-2 text-xs font-semibold text-[#73758A] dark:text-gray-400">
                  Befree Intelligence Engine • Real-time Statement Analysis
                </span>
              </div>
              <span className="text-xs font-mono font-medium text-[#12B886] bg-[#12B886]/10 px-2.5 py-1 rounded-md">
                100% Deterministic & Private
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="p-4 rounded-xl bg-[#F7F8FC] dark:bg-[#0F0F1A] border border-[#E9EAF2] dark:border-gray-800">
                <span className="text-xs text-[#73758A] font-medium">Total Volume Extracted</span>
                <div className="text-2xl font-bold text-[#17172B] dark:text-white mt-1">₹1,95,000.00</div>
                <span className="text-[11px] text-[#12B886] font-medium mt-1 inline-block">↑ Verified With Opening Bal</span>
              </div>
              <div className="p-4 rounded-xl bg-[#F7F8FC] dark:bg-[#0F0F1A] border border-[#E9EAF2] dark:border-gray-800">
                <span className="text-xs text-[#73758A] font-medium">Auto-Categorization Rate</span>
                <div className="text-2xl font-bold text-[#6C5CE7] mt-1">98.4%</div>
                <span className="text-[11px] text-gray-500 font-medium mt-1 inline-block">Hybrid Rule + LinearSVC</span>
              </div>
              <div className="p-4 rounded-xl bg-[#F7F8FC] dark:bg-[#0F0F1A] border border-[#E9EAF2] dark:border-gray-800">
                <span className="text-xs text-[#73758A] font-medium">Mathematical Reconciliation</span>
                <div className="text-2xl font-bold text-[#12B886] mt-1">Exact Match</div>
                <span className="text-[11px] text-[#12B886] font-medium mt-1 inline-block">Opening + Cr - Dr = Closing</span>
              </div>
            </div>

            <div className="rounded-lg bg-[#F7F8FC] dark:bg-[#0F0F1A] p-4 text-xs font-mono text-[#73758A] dark:text-gray-400 flex flex-col gap-2">
              <div className="flex justify-between items-center text-[#17172B] dark:text-gray-200 font-semibold border-b border-gray-200 dark:border-gray-800 pb-2">
                <span>Date & Narration</span>
                <span>Category Assigned</span>
                <span>Amount (INR)</span>
              </div>
              <div className="flex justify-between items-center">
                <span>2024-01-02 SALARY CREDIT JAN 2024</span>
                <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">Salary (0.95 conf)</span>
                <span className="text-emerald-600 font-bold">+₹75,000.00</span>
              </div>
              <div className="flex justify-between items-center">
                <span>2024-01-03 UPI/SWIGGY/FOOD ORDER</span>
                <span className="px-2 py-0.5 rounded bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300">Food & Dining</span>
                <span className="text-red-500 font-bold">-₹450.00</span>
              </div>
              <div className="flex justify-between items-center">
                <span>2024-01-04 NEFT/RENT PAYMENT/LANDLORD</span>
                <span className="px-2 py-0.5 rounded bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300">Rent</span>
                <span className="text-red-500 font-bold">-₹15,000.00</span>
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      {/* Feature Value Props */}
      <section className="relative z-10 max-w-6xl mx-auto px-6 py-16 border-t border-[#E9EAF2] dark:border-gray-800">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="p-6 rounded-2xl bg-white dark:bg-[#161626] border border-[#E9EAF2] dark:border-gray-800 shadow-sm">
            <div className="w-12 h-12 rounded-xl bg-[#6C5CE7]/10 text-[#6C5CE7] flex items-center justify-center mb-4">
              <Cpu className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-[#17172B] dark:text-white mb-2">Non-LLM Architecture</h3>
            <p className="text-sm text-[#73758A] dark:text-gray-400 leading-relaxed">
              Deterministic, privacy-preserving classification powered by character n-gram TF-IDF vectorizers and Linear Support Vector Machines. No high API costs or hallucination risk.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-white dark:bg-[#161626] border border-[#E9EAF2] dark:border-gray-800 shadow-sm">
            <div className="w-12 h-12 rounded-xl bg-teal-500/10 text-teal-500 flex items-center justify-center mb-4">
              <TrendingUp className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-[#17172B] dark:text-white mb-2">Automated Balance Auditing</h3>
            <p className="text-sm text-[#73758A] dark:text-gray-400 leading-relaxed">
              Guarantees data integrity by reconciling opening and closing balances across complex multi-page statements with detailed tolerance verification.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-white dark:bg-[#161626] border border-[#E9EAF2] dark:border-gray-800 shadow-sm">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-500 flex items-center justify-center mb-4">
              <FileSpreadsheet className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-[#17172B] dark:text-white mb-2">Executive Export Suite</h3>
            <p className="text-sm text-[#73758A] dark:text-gray-400 leading-relaxed">
              Export rich 3-sheet Excel spreadsheets formatted with freeze panes, custom conditional highlighting, and categorical breakdowns ready for accounting audits.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-[#E9EAF2] dark:border-gray-800 py-8 text-center text-xs text-[#73758A] dark:text-gray-400">
        Befree Automation Internship • Technical Assessment Round 2 • Statement Intelligence System
      </footer>
    </div>
  );
};
