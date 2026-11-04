import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  UploadCloud, FileText, CheckCircle2, AlertCircle, 
  Lock, RefreshCw, FileUp, Sparkles, Check 
} from 'lucide-react';
import confetti from 'canvas-confetti';
import { ProcessResponse } from '../types';

interface UploadModalProps {
  onProcessComplete: (data: ProcessResponse) => void;
  onCancel?: () => void;
}

export const UploadModal: React.FC<UploadModalProps> = ({ onProcessComplete, onCancel }) => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [password, setPassword] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStage, setCurrentStage] = useState(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const stages = [
    'Validating PDF structure and integrity',
    'Detecting format (Text layer vs. Scanned image)',
    'Extracting account-holder details & bank headers',
    'Parsing tabular transactions & stitching rows',
    'Auditing Opening + Credit - Debit = Closing balances',
    'Classifying transactions (Heuristic rules & LinearSVC)',
    'Synthesizing analytics and multi-sheet exports',
  ];

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const filesArray = Array.from(e.dataTransfer.files).filter(
        (file) => file.type === 'application/pdf' || file.name.endsWith('.pdf')
      );
      if (filesArray.length === 0) {
        setErrorMessage('Only PDF bank statements are supported.');
        return;
      }
      setSelectedFiles((prev) => [...prev, ...filesArray]);
      setErrorMessage(null);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const filesArray = Array.from(e.target.files);
      setSelectedFiles((prev) => [...prev, ...filesArray]);
      setErrorMessage(null);
    }
  };

  const loadSample = async (bank: 'sbi' | 'hdfc') => {
    const filename = bank === 'sbi' ? 'sbi_statement_jan2024.pdf' : 'hdfc_statement_feb2024.pdf';
    try {
      const res = await fetch(`/api/sample-files/download/${filename}`);
      if (!res.ok) throw new Error('Sample not found');
      const blob = await res.blob();
      const file = new File([blob], filename, { type: 'application/pdf' });
      setSelectedFiles([file]);
      setErrorMessage(null);
    } catch (err) {
      setErrorMessage('Could not load sample file from server.');
    }
  };

  const handleUploadAndProcess = async () => {
    if (selectedFiles.length === 0) {
      setErrorMessage('Please select or drag at least one bank statement PDF.');
      return;
    }

    setIsProcessing(true);
    setErrorMessage(null);
    setCurrentStage(0);

    // Progress timeline simulation synced with backend
    const interval = setInterval(() => {
      setCurrentStage((prev) => (prev < stages.length - 1 ? prev + 1 : prev));
    }, 450);

    const formData = new FormData();
    selectedFiles.forEach((file) => {
      formData.append('files', file);
    });
    if (password) {
      formData.append('password', password);
    }

    try {
      const res = await fetch('/api/process', {
        method: 'POST',
        body: formData,
      });

      clearInterval(interval);

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || 'Failed to process statement');
      }

      const data: ProcessResponse = await res.json();
      setCurrentStage(stages.length - 1);

      if (!data.success && (!data.transactions || data.transactions.length === 0)) {
        throw new Error(data.message || 'No transactions could be extracted.');
      }

      confetti({
        particleCount: 80,
        spread: 60,
        origin: { y: 0.6 },
      });

      setTimeout(() => {
        setIsProcessing(false);
        onProcessComplete(data);
      }, 700);
    } catch (err: any) {
      clearInterval(interval);
      setIsProcessing(false);
      setErrorMessage(err.message || 'An error occurred during processing.');
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-4">
      <div className="bg-white dark:bg-[#161626] border border-[#E9EAF2] dark:border-gray-800 rounded-3xl p-8 shadow-xl shadow-gray-200/50 dark:shadow-none transition-colors">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-[#17172B] dark:text-white">
              Upload Bank Statement
            </h2>
            <p className="text-sm text-[#73758A] dark:text-gray-400 mt-1">
              Supports both digital text-based e-statements & scanned physical statements
            </p>
          </div>
          <span className="text-xs font-semibold px-3 py-1 rounded-full bg-[#6C5CE7]/10 text-[#6C5CE7] border border-[#6C5CE7]/20">
            Multi-Bank Ingestion
          </span>
        </div>

        {/* Drag and drop zone */}
        {!isProcessing && (
          <>
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`relative border-2 border-dashed rounded-2xl p-10 text-center transition-all cursor-pointer ${
                isDragging
                  ? 'border-[#6C5CE7] bg-[#6C5CE7]/5 scale-[0.99]'
                  : 'border-gray-300 dark:border-gray-700 hover:border-[#6C5CE7] hover:bg-[#F7F8FC] dark:hover:bg-[#1A1A2E]'
              }`}
            >
              <input
                type="file"
                multiple
                accept=".pdf,application/pdf"
                onChange={handleFileChange}
                className="absolute inset-0 opacity-0 cursor-pointer"
              />
              <div className="w-16 h-16 rounded-2xl bg-[#6C5CE7]/10 text-[#6C5CE7] flex items-center justify-center mx-auto mb-4">
                <UploadCloud className="w-8 h-8" />
              </div>
              <h4 className="text-base font-bold text-[#17172B] dark:text-white mb-1">
                Drag and drop your PDF statement(s) here
              </h4>
              <p className="text-xs text-[#73758A] dark:text-gray-400 mb-4">
                Or click to browse from your computer (Up to 50MB per file)
              </p>

              {/* Sample statement quick buttons */}
              <div className="inline-flex items-center gap-2 p-1 rounded-xl bg-gray-100 dark:bg-gray-800 text-xs z-10 relative">
                <span className="text-gray-500 font-medium px-2">Try with samples:</span>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    loadSample('sbi');
                  }}
                  className="px-2.5 py-1 rounded-lg bg-white dark:bg-[#161626] text-[#6C5CE7] font-semibold hover:shadow-sm transition-all"
                >
                  SBI Statement
                </button>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    loadSample('hdfc');
                  }}
                  className="px-2.5 py-1 rounded-lg bg-white dark:bg-[#161626] text-[#6C5CE7] font-semibold hover:shadow-sm transition-all"
                >
                  HDFC Statement
                </button>
              </div>
            </div>

            {/* Selected Files List */}
            {selectedFiles.length > 0 && (
              <div className="mt-6 space-y-2">
                <span className="text-xs font-semibold text-[#17172B] dark:text-gray-300">
                  Selected Files ({selectedFiles.length}):
                </span>
                <div className="space-y-2 max-h-40 overflow-y-auto pr-1">
                  {selectedFiles.map((f, i) => (
                    <div
                      key={i}
                      className="flex items-center justify-between p-3 rounded-xl bg-[#F7F8FC] dark:bg-[#1A1A2E] border border-[#E9EAF2] dark:border-gray-800 text-xs"
                    >
                      <div className="flex items-center gap-2.5">
                        <FileText className="w-4 h-4 text-[#6C5CE7]" />
                        <span className="font-semibold text-[#17172B] dark:text-gray-200">
                          {f.name}
                        </span>
                        <span className="text-gray-400">({(f.size / 1024).toFixed(1)} KB)</span>
                      </div>
                      <button
                        type="button"
                        onClick={() => setSelectedFiles(selectedFiles.filter((_, idx) => idx !== i))}
                        className="text-gray-400 hover:text-red-500 font-bold px-2 py-0.5"
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Password input */}
            <div className="mt-5">
              <label className="block text-xs font-semibold text-[#73758A] dark:text-gray-300 mb-1.5 flex items-center gap-1.5">
                <Lock className="w-3.5 h-3.5" /> PDF Password (if protected)
              </label>
              <input
                type="password"
                placeholder="Leave empty if file is unprotected"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl text-xs sm:text-sm bg-[#F7F8FC] dark:bg-[#1A1A2E] border border-[#E9EAF2] dark:border-gray-800 text-[#17172B] dark:text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#6C5CE7]/30"
              />
            </div>

            {/* Error Message */}
            {errorMessage && (
              <div className="mt-4 p-3.5 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 text-xs text-red-600 dark:text-red-400 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMessage}</span>
              </div>
            )}

            {/* Action Buttons */}
            <div className="mt-8 flex items-center justify-end gap-3">
              {onCancel && (
                <button
                  type="button"
                  onClick={onCancel}
                  className="px-5 py-2.5 rounded-xl border border-gray-300 dark:border-gray-700 text-xs sm:text-sm font-semibold text-[#73758A] hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                >
                  Cancel
                </button>
              )}
              <button
                type="button"
                onClick={handleUploadAndProcess}
                disabled={selectedFiles.length === 0}
                className="px-6 py-3 rounded-xl bg-[#6C5CE7] hover:bg-[#5541C7] disabled:opacity-50 text-white text-xs sm:text-sm font-semibold shadow-lg shadow-[#6C5CE7]/30 transition-all flex items-center gap-2"
              >
                <Sparkles className="w-4 h-4" /> Start Intelligent Extraction
              </button>
            </div>
          </>
        )}

        {/* Processing Animation Screen */}
        {isProcessing && (
          <div className="py-8">
            <div className="text-center mb-8">
              <div className="w-16 h-16 rounded-2xl bg-[#6C5CE7]/10 text-[#6C5CE7] flex items-center justify-center mx-auto mb-4 animate-bounce">
                <RefreshCw className="w-8 h-8 animate-spin" />
              </div>
              <h3 className="text-xl font-bold text-[#17172B] dark:text-white">
                Processing Financial Statement
              </h3>
              <p className="text-xs text-[#73758A] dark:text-gray-400 mt-1">
                Applying non-LLM OCR, table boundary heuristics & classification
              </p>
            </div>

            {/* Processing Timeline */}
            <div className="space-y-3 max-w-lg mx-auto">
              {stages.map((stg, idx) => {
                const isDone = idx < currentStage;
                const isCurrent = idx === currentStage;

                return (
                  <div
                    key={idx}
                    className={`flex items-center gap-3 p-3 rounded-xl border text-xs transition-all ${
                      isDone
                        ? 'bg-emerald-50 dark:bg-emerald-950/30 border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300'
                        : isCurrent
                        ? 'bg-purple-50 dark:bg-purple-950/40 border-[#6C5CE7] text-[#6C5CE7] font-semibold scale-[1.02] shadow-sm'
                        : 'bg-gray-50 dark:bg-gray-800/40 border-transparent text-gray-400'
                    }`}
                  >
                    <div className="shrink-0">
                      {isDone ? (
                        <Check className="w-4 h-4 text-[#12B886]" />
                      ) : isCurrent ? (
                        <div className="w-4 h-4 rounded-full border-2 border-[#6C5CE7] border-t-transparent animate-spin" />
                      ) : (
                        <div className="w-4 h-4 rounded-full border border-gray-300 dark:border-gray-700" />
                      )}
                    </div>
                    <span className="flex-1">{stg}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
