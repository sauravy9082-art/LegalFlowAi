import React, { useState, useEffect, useRef } from 'react';
import { documentAPI } from '../services/api';
import { GitCompare, Loader2, CheckCircle2, AlertTriangle, FolderOpen } from 'lucide-react';

export const Compare = () => {
  const [documents, setDocuments] = useState([]);
  const [docA, setDocA] = useState('');
  const [docB, setDocB] = useState('');
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploadingA, setUploadingA] = useState(false);
  const [uploadingB, setUploadingB] = useState(false);

  const fileInputRefA = useRef(null);
  const fileInputRefB = useRef(null);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const res = await documentAPI.list();
      setDocuments(res.data || []);
    } catch (err) {
      console.error('Error fetching documents for comparison:', err);
    }
  };

  const handleFileUpload = async (file, targetSlot) => {
    if (!file) return;

    if (targetSlot === 'A') setUploadingA(true);
    else setUploadingB(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const res = await documentAPI.upload(formData);
      const newDoc = res.data;

      const updatedList = await documentAPI.list();
      setDocuments(updatedList.data || []);

      if (targetSlot === 'A') {
        setDocA(newDoc.id);
      } else {
        setDocB(newDoc.id);
      }
    } catch (err) {
      alert('Failed to upload document from file manager.');
    } finally {
      if (targetSlot === 'A') setUploadingA(false);
      else setUploadingB(false);
    }
  };

  const handleCompare = async (e) => {
    e.preventDefault();
    if (!docA || !docB || docA === docB) {
      alert('Please select two distinct contract documents to compare.');
      return;
    }

    setLoading(true);
    try {
      const res = await documentAPI.compare({ document_id_a: docA, document_id_b: docB });
      setComparison(res.data);
    } catch (err) {
      alert('Comparison failed. Please ensure both documents have been uploaded.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-xl font-bold text-[#17202A] flex items-center gap-2.5 tracking-tight">
          <GitCompare className="w-5 h-5 text-[#2F5D73]" />
          Side-by-Side Document & Clause Comparison
        </h1>
        <p className="text-xs text-[#64748B] mt-1">
          Select uploaded agreements or open your File Manager to pick contract files directly from your computer.
        </p>
      </div>

      {/* Select / Upload Form */}
      <form onSubmit={handleCompare} className="bg-[#FFFFFF] border border-[#D9D6CC] p-6 rounded-lg shadow-2xs mb-8 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Document A Column */}
          <div className="bg-[#F4F1E8] p-5 border border-[#D9D6CC] rounded-lg space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold text-[#17202A] uppercase tracking-wider">
                Original Baseline (Version A)
              </label>
            </div>

            {/* File Manager Pick Box */}
            <div 
              onClick={() => fileInputRefA.current?.click()}
              className="p-4 border-2 border-dashed border-[#D9D6CC] hover:border-[#163A59] bg-[#FFFFFF] hover:bg-slate-50 rounded-lg cursor-pointer text-center transition-colors group shadow-2xs"
            >
              {uploadingA ? (
                <div className="flex items-center justify-center gap-2 text-xs text-[#17202A] font-medium">
                  <Loader2 className="w-4 h-4 animate-spin text-[#163A59]" />
                  <span>Uploading from File Manager...</span>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-1">
                  <FolderOpen className="w-5 h-5 text-[#0F766E] group-hover:scale-105 transition-transform" />
                  <span className="text-xs font-bold text-[#17202A]">Open File Manager & Pick Document A</span>
                  <span className="text-[10px] text-[#64748B]">Supports .pdf, .docx, .txt</span>
                </div>
              )}
            </div>

            <input
              ref={fileInputRefA}
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={(e) => handleFileUpload(e.target.files[0], 'A')}
              className="hidden"
            />

            <div className="relative">
              <div className="text-[10px] text-[#64748B] font-bold mb-1 uppercase tracking-wider">Or Select from Vault:</div>
              <select
                value={docA}
                onChange={(e) => setDocA(e.target.value)}
                className="w-full bg-[#FFFFFF] border border-[#D9D6CC] rounded-lg p-2.5 text-xs text-[#17202A] focus:border-[#163A59] focus:outline-none transition-colors cursor-pointer shadow-2xs font-medium"
              >
                <option value="">-- Choose Document A --</option>
                {documents.map(d => {
                  const displayName = d.original_filename || d.filename || 'Contract.pdf';
                  return (
                    <option key={d.id} value={d.id}>
                      📄 {displayName} ({((d.file_size_bytes || 2048) / 1024).toFixed(1)} KB)
                    </option>
                  );
                })}
              </select>
            </div>
          </div>

          {/* Document B Column */}
          <div className="bg-[#F4F1E8] p-5 border border-[#D9D6CC] rounded-lg space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold text-[#17202A] uppercase tracking-wider">
                Revised Counterparty (Version B)
              </label>
            </div>

            {/* File Manager Pick Box */}
            <div 
              onClick={() => fileInputRefB.current?.click()}
              className="p-4 border-2 border-dashed border-[#D9D6CC] hover:border-[#163A59] bg-[#FFFFFF] hover:bg-slate-50 rounded-lg cursor-pointer text-center transition-colors group shadow-2xs"
            >
              {uploadingB ? (
                <div className="flex items-center justify-center gap-2 text-xs text-[#17202A] font-medium">
                  <Loader2 className="w-4 h-4 animate-spin text-[#163A59]" />
                  <span>Uploading from File Manager...</span>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-1">
                  <FolderOpen className="w-5 h-5 text-[#0F766E] group-hover:scale-105 transition-transform" />
                  <span className="text-xs font-bold text-[#17202A]">Open File Manager & Pick Document B</span>
                  <span className="text-[10px] text-[#64748B]">Supports .pdf, .docx, .txt</span>
                </div>
              )}
            </div>

            <input
              ref={fileInputRefB}
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={(e) => handleFileUpload(e.target.files[0], 'B')}
              className="hidden"
            />

            <div className="relative">
              <div className="text-[10px] text-[#64748B] font-bold mb-1 uppercase tracking-wider">Or Select from Vault:</div>
              <select
                value={docB}
                onChange={(e) => setDocB(e.target.value)}
                className="w-full bg-[#FFFFFF] border border-[#D9D6CC] rounded-lg p-2.5 text-xs text-[#17202A] focus:border-[#163A59] focus:outline-none transition-colors cursor-pointer shadow-2xs font-medium"
              >
                <option value="">-- Choose Document B --</option>
                {documents.map(d => {
                  const displayName = d.original_filename || d.filename || 'Contract.pdf';
                  return (
                    <option key={d.id} value={d.id}>
                      📄 {displayName} ({((d.file_size_bytes || 2048) / 1024).toFixed(1)} KB)
                    </option>
                  );
                })}
              </select>
            </div>
          </div>
        </div>

        <button
          type="submit"
          disabled={!docA || !docB || docA === docB || loading}
          className="w-full py-3 bg-[#163A59] hover:bg-[#102A43] disabled:opacity-30 text-white font-semibold text-xs rounded-lg shadow-2xs transition-colors flex items-center justify-center gap-2"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin text-white" /> : <GitCompare className="w-4 h-4" />}
          {loading ? 'Analyzing Clause Differences...' : 'Run Side-by-Side Clause Comparison'}
        </button>
      </form>

      {/* Results View */}
      {comparison && (
        <div className="space-y-6">
          {/* Summary Ribbon */}
          <div className="p-4 bg-[#FFFFFF] border border-[#D9D6CC] rounded-lg flex flex-wrap items-center justify-between gap-4 shadow-2xs">
            <div>
              <h3 className="text-sm font-bold text-[#17202A] mb-0.5">Side-by-Side Clause Comparison Summary</h3>
              <p className="text-xs text-[#64748B]">
                Comparing Baseline <strong>{comparison.document_a?.original_filename || 'Version A'}</strong> vs Counterparty <strong>{comparison.document_b?.original_filename || 'Version B'}</strong>
              </p>
            </div>

            <div className="flex items-center gap-3">
              <span className="px-2.5 py-1 bg-amber-50 text-[#D97706] border border-amber-200 rounded text-xs font-bold font-mono">
                MODIFIED: {comparison.modified_clauses?.length || 0}
              </span>
              <span className="px-2.5 py-1 bg-emerald-50 text-[#15803D] border border-emerald-200 rounded text-xs font-bold font-mono">
                ADDED: {comparison.added_clauses?.length || 0}
              </span>
              <span className="px-2.5 py-1 bg-rose-50 text-[#C62828] border border-rose-200 rounded text-xs font-bold font-mono">
                REMOVED: {comparison.removed_clauses?.length || 0}
              </span>
              <span className="px-2.5 py-1 bg-[#EAE6DC] text-[#17202A] border border-[#D9D6CC] rounded text-xs font-bold font-mono">
                UNCHANGED: {comparison.unchanged_clauses?.length || 0}
              </span>
              <span className="px-3 py-1 bg-[#163A59] text-white rounded-md text-xs font-bold font-mono shadow-2xs">
                Similarity: {((comparison.similarity_score || 0.85) * 100).toFixed(0)}%
              </span>
            </div>
          </div>

          {/* 1. MODIFIED CLAUSES SECTION */}
          {comparison.modified_clauses && comparison.modified_clauses.length > 0 && (
            <div className="p-5 bg-[#FFFFFF] border border-[#D9D6CC] rounded-lg space-y-4 shadow-2xs">
              <div className="flex items-center justify-between border-b border-[#D9D6CC] pb-2">
                <div className="flex items-center gap-2 text-[#D97706] font-bold text-xs uppercase tracking-wider">
                  <GitCompare className="w-4 h-4 text-[#D97706]" /> Modified Clauses ({comparison.modified_clauses.length})
                </div>
                <span className="text-[11px] text-[#64748B] font-medium">Wording, numbers, or terms changed between versions</span>
              </div>

              <div className="space-y-4">
                {comparison.modified_clauses.map((item, idx) => (
                  <div key={idx} className="bg-[#F4F1E8] border border-[#D9D6CC] rounded-lg p-4 space-y-2">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-bold text-[#D97706] bg-amber-50 border border-amber-200 px-2 py-0.5 rounded font-mono">
                        {item.category || 'Modified Clause'}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {/* Version A */}
                      <div className="p-3 bg-rose-50 border border-rose-200 rounded-md">
                        <div className="text-[10px] font-bold text-[#C62828] uppercase mb-1">Version A (Baseline Original):</div>
                        <p className="text-xs text-[#C62828] font-mono leading-relaxed">{item.text_a}</p>
                      </div>

                      {/* Version B */}
                      <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-md">
                        <div className="text-[10px] font-bold text-[#15803D] uppercase mb-1">Version B (Counterparty Revised):</div>
                        <p className="text-xs text-[#15803D] font-mono leading-relaxed">{item.text_b}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 2. ADDED & REMOVED CLAUSES GRID */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Added Clauses */}
            <div className="p-5 bg-[#FFFFFF] border border-[#D9D6CC] rounded-lg space-y-3 shadow-2xs">
              <div className="flex items-center gap-2 text-[#15803D] font-bold text-xs uppercase tracking-wider border-b border-[#D9D6CC] pb-2">
                <CheckCircle2 className="w-4 h-4 text-[#15803D]" /> Added Clauses in Version B ({comparison.added_clauses?.length || 0})
              </div>
              {(!comparison.added_clauses || comparison.added_clauses.length === 0) ? (
                <p className="text-xs text-[#64748B] italic">No new clauses inserted.</p>
              ) : (
                comparison.added_clauses.map((clauseText, i) => (
                  <div key={i} className="p-3 border-l-4 border-[#15803D] bg-emerald-50 text-[#15803D] rounded-r-md text-xs leading-relaxed font-mono">
                    • {clauseText}
                  </div>
                ))
              )}
            </div>

            {/* Removed Clauses */}
            <div className="p-5 bg-[#FFFFFF] border border-[#D9D6CC] rounded-lg space-y-3 shadow-2xs">
              <div className="flex items-center gap-2 text-[#C62828] font-bold text-xs uppercase tracking-wider border-b border-[#D9D6CC] pb-2">
                <AlertTriangle className="w-4 h-4 text-[#C62828]" /> Removed Terms from Version A ({comparison.removed_clauses?.length || 0})
              </div>
              {(!comparison.removed_clauses || comparison.removed_clauses.length === 0) ? (
                <p className="text-xs text-[#64748B] italic">No baseline terms removed.</p>
              ) : (
                comparison.removed_clauses.map((clauseText, i) => (
                  <div key={i} className="p-3 border-l-4 border-[#C62828] bg-rose-50 text-[#C62828] rounded-r-md text-xs leading-relaxed font-mono">
                    • {clauseText}
                  </div>
                ))
              )}
            </div>
          </div>

          {/* 3. UNCHANGED CLAUSES SECTION */}
          {comparison.unchanged_clauses && comparison.unchanged_clauses.length > 0 && (
            <div className="p-5 bg-[#FFFFFF] border border-[#D9D6CC] rounded-lg space-y-3 shadow-2xs">
              <div className="flex items-center justify-between border-b border-[#D9D6CC] pb-2">
                <span className="text-xs font-bold text-[#17202A] uppercase tracking-wider">
                  Unchanged Clauses ({comparison.unchanged_clauses.length})
                </span>
                <span className="text-[11px] text-[#64748B] font-medium">Identical in both versions</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {comparison.unchanged_clauses.map((uText, i) => (
                  <div key={i} className="p-3 bg-[#F4F1E8] border border-[#D9D6CC] rounded-md text-xs text-[#17202A] leading-relaxed font-mono truncate">
                    ✓ {uText}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
