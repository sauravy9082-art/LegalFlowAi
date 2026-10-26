import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { documentAPI } from '../services/api';
import { UploadCloud, FileText, AlertCircle, Loader2, Lock, ShieldCheck } from 'lucide-react';

export const Upload = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected) {
      setFile(selected);
      setError('');
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setError('');
    }
  };

  const parseUploadError = (err) => {
    if (!err.response) {
      return 'Backend server unreachable. Ensure FastAPI backend is running on http://localhost:8080.';
    }
    if (err.response.status === 404) {
      return 'Upload endpoint not found. Please ensure the LegalGuard AI backend is running on port 8080.';
    }
    if (err.response.status === 401) {
      return 'Session expired. Please refresh the page to renew your session and try again.';
    }
    const detail = err.response?.data?.detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) return detail.map(d => d.msg || JSON.stringify(d)).join(' | ');
    return 'Document upload failed. Please ensure file is valid PDF/DOCX and try again.';
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await documentAPI.upload(formData);
      const docId = res.data?.id;
      if (!docId) {
        throw new Error('Invalid response from server.');
      }
      navigate(`/documents/${docId}`);
    } catch (err) {
      setError(parseUploadError(err));
      setUploading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-6 py-10">
      <div className="bg-[#FFFFFF] border border-[#D9D6CC] p-8 rounded-lg shadow-2xs">
        <div className="text-center mb-8">
          <div className="inline-flex p-3 rounded-lg bg-[#102A43] text-white mb-3 shadow-2xs">
            <UploadCloud className="w-6 h-6 text-white" />
          </div>
          <h2 className="text-xl font-bold text-[#17202A] tracking-tight">Upload Legal Document</h2>
          <p className="text-xs text-[#64748B] mt-1">
            Automated clause extraction, risk assessment, and DOCX redlining engine.
          </p>
          <div className="flex items-center justify-center gap-2 mt-3">
            <span className="text-[10px] font-mono font-semibold px-2 py-0.5 bg-[#F4F1E8] border border-[#D9D6CC] rounded text-[#64748B]">PDF</span>
            <span className="text-[10px] font-mono font-semibold px-2 py-0.5 bg-[#F4F1E8] border border-[#D9D6CC] rounded text-[#64748B]">DOCX</span>
            <span className="text-[10px] font-mono font-semibold px-2 py-0.5 bg-[#F4F1E8] border border-[#D9D6CC] rounded text-[#64748B]">TXT</span>
            <span className="text-[10px] font-mono font-semibold px-2 py-0.5 bg-[#F4F1E8] border border-[#D9D6CC] rounded text-[#64748B]">OCR Scans</span>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-3.5 rounded-lg bg-rose-50 border border-rose-200 text-[#C62828] text-xs flex items-center gap-2.5 font-medium">
            <AlertCircle className="w-4 h-4 shrink-0 text-[#C62828]" />
            <span className="leading-snug">{error}</span>
          </div>
        )}

        <form onSubmit={handleUpload} className="space-y-6">
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-lg p-10 text-center transition-colors cursor-pointer ${
              file ? 'border-[#163A59] bg-[#F4F1E8]' : 'border-[#D9D6CC] bg-[#F4F1E8]/50 hover:border-[#163A59] hover:bg-[#F4F1E8]'
            }`}
          >
            <input
              type="file"
              onChange={handleFileChange}
              accept=".pdf,.docx,.doc,.txt,.png,.jpg,.jpeg"
              className="hidden"
              id="file-upload"
            />
            <label htmlFor="file-upload" className="cursor-pointer block">
              {file ? (
                <div className="flex flex-col items-center">
                  <div className="p-3 bg-[#163A59] text-white rounded-lg mb-2 shadow-2xs">
                    <FileText className="w-7 h-7" />
                  </div>
                  <span className="text-sm font-semibold text-[#17202A]">{file.name}</span>
                  <span className="text-xs text-[#64748B] mt-1 font-mono">{(file.size / 1024).toFixed(1)} KB</span>
                </div>
              ) : (
                <div className="flex flex-col items-center">
                  <UploadCloud className="w-9 h-9 text-[#0F766E] mb-3" />
                  <span className="text-xs font-semibold text-[#17202A]">Drag & drop your contract here, or click to browse</span>
                  <span className="text-[11px] text-[#64748B] mt-1">Max file size: 25MB</span>
                </div>
              )}
            </label>
          </div>

          <div className="p-3.5 bg-[#F4F1E8] rounded-lg border border-[#D9D6CC] text-xs text-[#17202A] flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-[#15803D]" />
              <span className="font-semibold text-[#17202A]">Air-Gapped Privacy & Local Storage</span>
            </div>
            <span className="text-[#64748B] text-[11px] font-mono">Zero External Data Leakage</span>
          </div>

          <button
            type="submit"
            disabled={!file || uploading}
            className="w-full py-3 bg-[#163A59] hover:bg-[#102A43] disabled:opacity-40 text-white font-semibold text-xs rounded-lg shadow-2xs transition-colors flex items-center justify-center gap-2"
          >
            {uploading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-white" />
                Uploading & Initializing Workspace...
              </>
            ) : (
              'Upload & Inspect Contract'
            )}
          </button>
        </form>
      </div>
    </div>
  );
};
