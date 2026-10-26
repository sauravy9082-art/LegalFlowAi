import React, { useState, useEffect } from 'react';
import { systemAPI } from '../services/api';
import { Lock, AlertCircle, ShieldCheck } from 'lucide-react';

export const Privacy = () => {
  const [ollamaStatus, setOllamaStatus] = useState(null);

  useEffect(() => {
    systemAPI.getOllamaStatus()
      .then(res => setOllamaStatus(res.data || {}))
      .catch(() => setOllamaStatus({ ollama_connected: false, ollama_active: false, status: 'disconnected' }));
  }, []);

  const isConnected = Boolean(
    ollamaStatus?.ollama_connected || 
    ollamaStatus?.ollama_active || 
    ollamaStatus?.status === 'connected'
  );

  const selectedModel = 
    ollamaStatus?.configured_model || 
    ollamaStatus?.ollama_model || 
    ollamaStatus?.model || 
    'llama3.1:8b';

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <div className="bg-white border border-[#D9D6CC] p-8 rounded-lg shadow-2xs space-y-8">
        {/* Header */}
        <div className="flex items-center gap-4 border-b border-[#D9D6CC] pb-6">
          <div className="p-3 bg-emerald-50 border border-emerald-200 text-[#15803D] rounded-lg shadow-2xs">
            <Lock className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-[#17202A] tracking-tight">Privacy Center & Enterprise Security Audit</h1>
            <p className="text-xs text-[#64748B] mt-1">
              Architecture audit matrix and verified local system status for LegalFlow AI.
            </p>
          </div>
        </div>

        {/* Security & Architecture Table */}
        <div className="bg-white border border-[#D9D6CC] rounded-lg overflow-hidden shadow-2xs">
          <div className="px-5 py-3 border-b border-[#D9D6CC] bg-[#102A43] flex items-center justify-between text-white">
            <h3 className="text-xs font-bold uppercase tracking-wider text-white">Security & Architecture Compliance Matrix</h3>
            <span className="text-[10px] font-mono text-[#B58B45] font-bold flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5 text-[#15803D]" /> Offline-Capable Verified
            </span>
          </div>

          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-[#D9D6CC] bg-[#EAE6DC]/60 text-[10px] uppercase font-bold text-[#17202A] tracking-wider">
                <th className="py-3 px-5">System Component</th>
                <th className="py-3 px-4">Engine / Provider</th>
                <th className="py-3 px-4">Implementation Status</th>
                <th className="py-3 px-5 text-right">Security Level</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#D9D6CC]/60 text-xs font-mono">
              {/* 1. AI Model Provider */}
              <tr className="hover:bg-[#EAE6DC]/40 transition-colors">
                <td className="py-3.5 px-5 font-bold text-[#17202A]">AI Model Provider</td>
                <td className="py-3.5 px-4 text-[#17202A]">Ollama — Local LLM</td>
                <td className="py-3.5 px-4 text-[#17202A] font-semibold">Active Local Daemon</td>
                <td className="py-3.5 px-5 text-right">
                  <span className="px-2 py-0.5 text-[9px] font-bold bg-[#EAE6DC] text-[#17202A] border border-[#D9D6CC] rounded uppercase">OLLAMA</span>
                </td>
              </tr>

              {/* 2. Ollama Connection */}
              <tr className="hover:bg-[#EAE6DC]/40 transition-colors">
                <td className="py-3.5 px-5 font-bold text-[#17202A]">Ollama Connection</td>
                <td className="py-3.5 px-4 text-[#17202A]">HTTP REST (localhost:11434)</td>
                <td className="py-3.5 px-4">
                  <div className="flex items-center gap-1.5">
                    <span className={`h-2 w-2 rounded-full ${isConnected ? 'bg-[#15803D]' : 'bg-[#D97706]'}`}></span>
                    <span className={isConnected ? 'text-[#15803D] font-semibold' : 'text-[#D97706] font-semibold'}>
                      {isConnected ? 'Connected' : 'Disconnected'}
                    </span>
                  </div>
                </td>
                <td className="py-3.5 px-5 text-right">
                  <span className={`px-2 py-0.5 text-[9px] font-bold rounded uppercase ${
                    isConnected
                      ? 'bg-emerald-50 text-[#15803D] border border-emerald-200'
                      : 'bg-amber-50 text-[#D97706] border border-amber-200'
                  }`}>
                    {isConnected ? 'CONNECTED' : 'DISCONNECTED'}
                  </span>
                </td>
              </tr>

              {/* 3. Selected Model */}
              <tr className="hover:bg-[#EAE6DC]/40 transition-colors">
                <td className="py-3.5 px-5 font-bold text-[#17202A]">Selected Model</td>
                <td className="py-3.5 px-4 text-[#17202A]">{selectedModel}</td>
                <td className="py-3.5 px-4 text-[#64748B]">Configured Local Instance</td>
                <td className="py-3.5 px-5 text-right">
                  <span className="px-2 py-0.5 text-[9px] font-bold bg-[#EAE6DC] text-[#17202A] border border-[#D9D6CC] rounded uppercase">
                    {selectedModel.split(':')[0]}
                  </span>
                </td>
              </tr>

              {/* 4. Document Storage */}
              <tr className="hover:bg-[#EAE6DC]/40 transition-colors">
                <td className="py-3.5 px-5 font-bold text-[#17202A]">Document Storage</td>
                <td className="py-3.5 px-4 text-[#17202A]">Local Disk (./storage/documents)</td>
                <td className="py-3.5 px-4 text-[#15803D] font-semibold">Local File Persistence</td>
                <td className="py-3.5 px-5 text-right">
                  <span className="px-2 py-0.5 text-[9px] font-bold bg-emerald-50 text-[#15803D] border border-emerald-200 rounded uppercase">LOCAL DISK</span>
                </td>
              </tr>

              {/* 5. Cloud Egress */}
              <tr className="hover:bg-[#EAE6DC]/40 transition-colors">
                <td className="py-3.5 px-5 font-bold text-[#17202A]">Cloud AI / External Uploads</td>
                <td className="py-3.5 px-4 text-[#17202A]">Disabled (Zero Cloud Egress)</td>
                <td className="py-3.5 px-4 text-[#C62828] font-semibold">External API Calls Blocked</td>
                <td className="py-3.5 px-5 text-right">
                  <span className="px-2 py-0.5 text-[9px] font-bold bg-rose-50 text-[#C62828] border border-rose-200 rounded uppercase">DISABLED</span>
                </td>
              </tr>

              {/* 6. OCR Processing */}
              <tr className="hover:bg-[#EAE6DC]/40 transition-colors">
                <td className="py-3.5 px-5 font-bold text-[#17202A]">OCR Processing</td>
                <td className="py-3.5 px-4 text-[#17202A]">PyMuPDF / Tesseract OCR</td>
                <td className="py-3.5 px-4 text-[#64748B]">Local Image & PDF Extractor</td>
                <td className="py-3.5 px-5 text-right">
                  <span className="px-2 py-0.5 text-[9px] font-bold bg-[#EAE6DC] text-[#17202A] border border-[#D9D6CC] rounded uppercase">LOCAL</span>
                </td>
              </tr>

              {/* 7. Database */}
              <tr className="hover:bg-[#EAE6DC]/40 transition-colors">
                <td className="py-3.5 px-5 font-bold text-[#17202A]">Database</td>
                <td className="py-3.5 px-4 text-[#17202A]">Local SQLite (legalflow.db)</td>
                <td className="py-3.5 px-4 text-[#64748B]">SQLAlchemy Async Engine</td>
                <td className="py-3.5 px-5 text-right">
                  <span className="px-2 py-0.5 text-[9px] font-bold bg-[#EAE6DC] text-[#17202A] border border-[#D9D6CC] rounded uppercase">LOCAL SQLITE</span>
                </td>
              </tr>

              {/* 8. Vector Database */}
              <tr className="hover:bg-[#EAE6DC]/40 transition-colors">
                <td className="py-3.5 px-5 font-bold text-[#17202A]">Vector Database</td>
                <td className="py-3.5 px-4 text-[#17202A]">Local ChromaDB (./chroma_db)</td>
                <td className="py-3.5 px-4 text-[#64748B]">Local HNSW Cosine Index</td>
                <td className="py-3.5 px-5 text-right">
                  <span className="px-2 py-0.5 text-[9px] font-bold bg-[#EAE6DC] text-[#17202A] border border-[#D9D6CC] rounded uppercase">LOCAL CHROMADB</span>
                </td>
              </tr>

              {/* 9. Internet Requirement */}
              <tr className="hover:bg-[#EAE6DC]/40 transition-colors">
                <td className="py-3.5 px-5 font-bold text-[#17202A]">Internet Required at Runtime</td>
                <td className="py-3.5 px-4 text-[#17202A]">No Network Connection Required*</td>
                <td className="py-3.5 px-4 text-[#15803D] font-semibold">100% Offline-Capable</td>
                <td className="py-3.5 px-5 text-right">
                  <span className="px-2 py-0.5 text-[9px] font-bold bg-emerald-50 text-[#15803D] border border-emerald-200 rounded uppercase">OFFLINE-CAPABLE</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Security Commitments */}
        <div className="space-y-3 pt-4 border-t border-[#D9D6CC]">
          <h3 className="text-xs font-bold text-[#17202A] uppercase tracking-wider">Enterprise Architecture Commitments</h3>
          <div className="space-y-2 text-xs text-[#17202A] leading-relaxed">
            <p className="flex items-start gap-2">
              <span className="text-[#15803D] font-bold">•</span>
              <span><strong>Zero External Transmission:</strong> Contracts uploaded to LegalFlow AI are never transmitted to external cloud services or third-party AI APIs.</span>
            </p>
            <p className="flex items-start gap-2">
              <span className="text-[#15803D] font-bold">•</span>
              <span><strong>Local Disk & Database:</strong> Extracted clauses and vector embeddings remain on your host machine filesystem.</span>
            </p>
            <p className="flex items-start gap-2">
              <span className="text-[#15803D] font-bold">•</span>
              <span><strong>Offline Fallback Guarantee:</strong> Heuristic pattern rules and offline RAG ensure 100% functionality even when local LLM services are disconnected.</span>
            </p>
          </div>

          <p className="text-[11px] text-[#64748B] italic pt-2 border-t border-[#D9D6CC] font-mono">
            *After required local models and software dependencies are installed on the host machine.
          </p>
        </div>

        {/* Mandatory Legal Disclaimer */}
        <div className="p-3.5 bg-amber-50 rounded-lg border border-amber-200 text-xs text-[#D97706] flex items-center gap-2 font-mono font-medium">
          <AlertCircle className="w-4 h-4 text-[#D97706] shrink-0" />
          <span>
            "LegalFlow AI is an informational document-analysis tool and does not replace a qualified lawyer or provide legal representation."
          </span>
        </div>
      </div>
    </div>
  );
};
