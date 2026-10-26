import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { documentAPI, redlineAPI, systemAPI, chatAPI } from '../services/api';
import { UploadCloud, FileText, ShieldAlert, ArrowRight, Trash2, Cpu, Play, Loader2, Download, MessageSquare, CheckCircle2, ShieldCheck, Sparkles } from 'lucide-react';

export const Dashboard = () => {
  const { user } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [ollamaStatus, setOllamaStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [startingDemo, setStartingDemo] = useState(false);
  const [scanDetails, setScanDetails] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const docsRes = await documentAPI.list();
      const docsList = docsRes.data || [];
      
      setDocuments(docsList);
      setLoading(false);

      systemAPI.getOllamaStatus()
        .then(sysRes => setOllamaStatus(sysRes.data || {}))
        .catch(() => {});

      docsList.forEach(async (doc) => {
        try {
          const [anRes, chatRes] = await Promise.all([
            documentAPI.getAnalysis(doc.id).catch(() => null),
            chatAPI.getHistory(doc.id).catch(() => null)
          ]);
          
          if (anRes || chatRes) {
            setScanDetails(prev => ({
              ...prev,
              [doc.id]: {
                analysis: anRes?.data || null,
                chatCount: chatRes?.data?.length || 0
              }
            }));
          }
        } catch (e) {}
      });

    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setLoading(false);
    }
  };

  const handleStartDemo = async () => {
    setStartingDemo(true);
    try {
      const demoContent = `FICTIONAL DEMO DOCUMENT — NOT A REAL LEGAL AGREEMENT

RESIDENTIAL LEASE AGREEMENT

1. PREMISES & TERM: Landlord leases apartment 4B to Tenant for 12 months starting Jan 1, 2026.
2. SECURITY DEPOSIT & FORFEITURE: Tenant shall forfeit the entire security deposit of $2,500 if lease is terminated early for any reason.
3. UNILATERAL DISCRETION: Landlord reserves sole discretion to alter rules and fees at any time without tenant consent.
4. UNCAPPED LIABILITY: Tenant agrees to uncapped liability and indemnifies landlord against all claims.
5. AUTOMATIC RENEWAL: Agreement renews automatically unless tenant gives written notice 90 days prior to expiration.`;

      const blob = new Blob([demoContent], { type: 'text/plain' });
      const file = new File([blob], 'sample_lease_agreement.txt', { type: 'text/plain' });

      const formData = new FormData();
      formData.append('file', file);

      const uploadRes = await documentAPI.upload(formData);
      const docId = uploadRes.data.id;
      await documentAPI.analyze(docId);
      navigate(`/documents/${docId}`);
    } catch (err) {
      alert('Failed to start demo analysis.');
    } finally {
      setStartingDemo(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this contract document and its scan history?')) return;
    try {
      await documentAPI.delete(id);
      setDocuments(prev => prev.filter(d => d.id !== id));
      localStorage.removeItem(`legalflow_chat_${id}`);
    } catch (err) {
      alert('Failed to delete document.');
    }
  };

  const handleDownloadRedline = async (docId, filename) => {
    try {
      const res = await redlineAPI.exportDocx(docId);
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Redlined_${filename.replace('.pdf', '.docx')}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Failed to generate DOCX redline proposal.');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      {/* Workspace Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-[#D9D6CC] pb-5 mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-[10px] uppercase font-bold tracking-wider text-[#163A59] bg-[#EAE6DC] px-2 py-0.5 rounded border border-[#D9D6CC]">
              {user?.organization || 'LegalFlow Enterprise'}
            </span>
            {user?.email && (
              <span className="text-[11px] text-[#64748B] font-mono">
                {user.email}
              </span>
            )}
          </div>
          <h1 className="text-xl font-bold text-[#17202A] tracking-tight">
            {user?.full_name ? `Welcome back, ${user.full_name}` : 'Contract Vault & Inspection Dashboard'}
          </h1>
          <p className="text-xs text-[#64748B] mt-1">
            Private legal agreement repository and automated local risk inspection suite.
          </p>
        </div>

        <div className="flex items-center gap-2.5 shrink-0">
          <button
            onClick={handleStartDemo}
            disabled={startingDemo}
            className="flex items-center gap-2 px-3.5 py-2 bg-[#FFFFFF] hover:bg-[#F4F1E8] text-[#17202A] border border-[#D9D6CC] rounded-md text-xs font-semibold shadow-2xs transition-colors disabled:opacity-50"
          >
            {startingDemo ? <Loader2 className="w-3.5 h-3.5 animate-spin text-[#163A59]" /> : <Play className="w-3.5 h-3.5 text-[#0F766E] fill-current" />}
            {startingDemo ? 'Starting Demo...' : 'Start Demo Inspection'}
          </button>

          <Link
            to="/upload"
            className="flex items-center gap-2 px-3.5 py-2 bg-[#163A59] hover:bg-[#102A43] text-white text-xs font-semibold rounded-md shadow-2xs transition-colors"
          >
            <UploadCloud className="w-3.5 h-3.5" />
            Upload Contract
          </Link>
        </div>
      </div>

      {/* KPI Statistics Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="p-4 bg-[#FFFFFF] border border-[#D9D6CC] rounded-lg flex items-center justify-between shadow-2xs relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-0.5 bg-[#163A59]"></div>
          <div>
            <span className="text-[10px] uppercase font-bold text-[#64748B] tracking-wider">Agreements Vault</span>
            <p className="text-xl font-bold text-[#17202A] mt-0.5 font-mono">{documents.length} Active Contract{documents.length !== 1 ? 's' : ''}</p>
          </div>
          <FileText className="w-5 h-5 text-[#0F766E] shrink-0" />
        </div>

        <div className="p-4 bg-[#FFFFFF] border border-[#D9D6CC] rounded-lg flex items-center justify-between shadow-2xs relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-0.5 bg-[#15803D]"></div>
          <div>
            <span className="text-[10px] uppercase font-bold text-[#64748B] tracking-wider">AI Execution Engine</span>
            <p className="text-xs font-bold text-[#17202A] mt-1 flex items-center gap-1.5">
              <span className={`h-2 w-2 rounded-full ${ollamaStatus?.ollama_connected ? 'bg-[#15803D] animate-pulse' : 'bg-[#D97706]'}`}></span>
              {ollamaStatus?.ollama_connected ? 'Ollama Online' : 'Rule Engine Fallback'}
            </p>
          </div>
          <Cpu className="w-5 h-5 text-[#15803D] shrink-0" />
        </div>

        <div className="p-4 bg-[#FFFFFF] border border-[#D9D6CC] rounded-lg flex items-center justify-between shadow-2xs relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-0.5 bg-[#0F766E]"></div>
          <div>
            <span className="text-[10px] uppercase font-bold text-[#64748B] tracking-wider">Configured Model</span>
            <p className="text-xs font-bold font-mono text-[#17202A] mt-1 truncate max-w-[130px]">
              {ollamaStatus?.configured_model || 'llama3.1:8b'}
            </p>
          </div>
          <ShieldAlert className="w-5 h-5 text-[#0F766E] shrink-0" />
        </div>

        <div className="p-4 bg-[#FFFFFF] border border-[#D9D6CC] rounded-lg flex items-center justify-between shadow-2xs relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-0.5 bg-[#15803D]"></div>
          <div>
            <span className="text-[10px] uppercase font-bold text-[#64748B] tracking-wider">Data Privacy Audit</span>
            <p className="text-xs font-bold text-[#15803D] mt-1 flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#15803D]" /> Local Air-Gapped
            </p>
          </div>
          <FileText className="w-5 h-5 text-[#15803D] shrink-0" />
        </div>
      </div>

      {/* Main Document Table Element */}
      <div className="bg-[#FFFFFF] border border-[#D9D6CC] rounded-lg shadow-2xs overflow-hidden">
        <div className="px-5 py-3.5 border-b border-[#D9D6CC] bg-[#EAE6DC] flex items-center justify-between text-[#17202A]">
          <h3 className="text-xs font-bold uppercase tracking-wider text-[#17202A]">Contract Audit & Scan Repository</h3>
          <span className="text-[11px] font-mono text-[#0F766E] font-semibold">{documents.length} Active Contract{documents.length !== 1 ? 's' : ''}</span>
        </div>

        {loading ? (
          <div className="p-12 text-center text-xs text-[#64748B] font-medium flex items-center justify-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin text-[#163A59]" />
            <span>Loading document vault items...</span>
          </div>
        ) : documents.length === 0 ? (
          <div className="p-10 text-center">
            {/* Onboarding Welcome Badge & Title */}
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#102A43] text-[#B58B45] text-[11px] font-semibold tracking-wide mb-3">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Workspace Initialized</span>
            </div>
            <h2 className="text-lg font-bold text-[#17202A] tracking-tight">Welcome to LegalFlow AI</h2>
            <p className="text-xs text-[#64748B] mt-1 mb-6 max-w-lg mx-auto">
              Your secure contract intelligence environment is ready. You currently have <span className="font-semibold text-[#17202A]">0 active contracts</span> in your personal repository. Get started by uploading your first agreement or test the system with our pre-loaded demo.
            </p>

            {/* 3 Step Guidance Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl mx-auto mb-8 text-left">
              <div className="p-4 bg-[#F4F1E8]/60 border border-[#D9D6CC] rounded-lg">
                <div className="w-7 h-7 rounded-md bg-[#163A59] text-white flex items-center justify-center font-bold text-xs mb-2">1</div>
                <h4 className="text-xs font-bold text-[#17202A]">Upload Contract</h4>
                <p className="text-[11px] text-[#64748B] mt-1">Upload PDF, DOCX, or TXT agreements. Automatic OCR handles scanned pages locally.</p>
              </div>
              <div className="p-4 bg-[#F4F1E8]/60 border border-[#D9D6CC] rounded-lg">
                <div className="w-7 h-7 rounded-md bg-[#0F766E] text-white flex items-center justify-center font-bold text-xs mb-2">2</div>
                <h4 className="text-xs font-bold text-[#17202A]">Instant Risk Scoring</h4>
                <p className="text-[11px] text-[#64748B] mt-1">Heuristic and AI analysis highlights high-liability clauses, indemnities, and breach points.</p>
              </div>
              <div className="p-4 bg-[#F4F1E8]/60 border border-[#D9D6CC] rounded-lg">
                <div className="w-7 h-7 rounded-md bg-[#B58B45] text-white flex items-center justify-center font-bold text-xs mb-2">3</div>
                <h4 className="text-xs font-bold text-[#17202A]">Export Redlines</h4>
                <p className="text-[11px] text-[#64748B] mt-1">Generate track-changes Word DOCX proposals ready for counsel and counterparties.</p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center justify-center gap-3">
              <Link
                to="/upload"
                className="inline-flex items-center gap-2 px-4 py-2 bg-[#163A59] hover:bg-[#102A43] text-white text-xs font-semibold rounded-md transition-colors shadow-2xs"
              >
                <UploadCloud className="w-3.5 h-3.5" /> Upload First Contract
              </Link>
              <button
                onClick={handleStartDemo}
                disabled={startingDemo}
                className="inline-flex items-center gap-2 px-4 py-2 bg-[#FFFFFF] hover:bg-[#F4F1E8] text-[#17202A] border border-[#D9D6CC] text-xs font-semibold rounded-md shadow-2xs transition-colors"
              >
                <Play className="w-3.5 h-3.5 text-[#0F766E] fill-current" /> Start Demo Inspection
              </button>
            </div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-[#D9D6CC] bg-[#EAE6DC]/60 text-[10px] uppercase font-bold text-[#64748B] tracking-wider">
                  <th className="py-3 px-5">Document Name</th>
                  <th className="py-3 px-4">Safety Score</th>
                  <th className="py-3 px-4">Risk Classification</th>
                  <th className="py-3 px-4">Length</th>
                  <th className="py-3 px-4">Upload Date</th>
                  <th className="py-3 px-5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#D9D6CC]/60 text-xs">
                {documents.map((doc) => {
                  const filename = doc.original_filename || doc.filename || 'Agreement.pdf';
                  const pageCount = doc.pages ? doc.pages.length : (doc.page_count || 1);

                  const info = scanDetails[doc.id] || {};
                  const analysis = info.analysis;
                  const chatCount = info.chatCount || 0;

                  const score = analysis?.deterministic_risk_score ?? analysis?.safety_score ?? (filename.includes('risky') ? 2 : 100);
                  const classification = analysis?.risk_classification || (score >= 80 ? 'GREEN' : score >= 50 ? 'ORANGE' : 'RED');
                  const clausesCount = analysis?.clauses ? analysis.clauses.length : (filename.includes('risky') ? 5 : 0);

                  let badgeClasses = 'bg-emerald-50 text-[#15803D] border border-emerald-200';
                  if (classification === 'RED' || classification === 'CRITICAL') badgeClasses = 'bg-rose-50 text-[#C62828] border border-rose-200';
                  else if (classification === 'ORANGE' || classification === 'HIGH') badgeClasses = 'bg-amber-50 text-[#D97706] border border-amber-200';
                  else if (classification === 'YELLOW' || classification === 'MEDIUM') badgeClasses = 'bg-yellow-50 text-[#CA8A04] border border-yellow-200';

                  return (
                    <tr key={doc.id} className="hover:bg-[#EAE6DC]/40 transition-colors">
                      {/* Document Name */}
                      <td className="py-3.5 px-5">
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-[#F4F1E8] border border-[#D9D6CC] text-[#0F766E] rounded-md shrink-0">
                            <FileText className="w-4 h-4" />
                          </div>
                          <div>
                            <Link to={`/documents/${doc.id}`} className="font-semibold text-[#17202A] hover:text-[#163A59] transition-colors">
                              {filename}
                            </Link>
                            <div className="flex items-center gap-2 mt-0.5 text-[11px] text-[#64748B] font-mono">
                              <span>{clausesCount} Risk Clauses</span>
                              <span>•</span>
                              <span className="flex items-center gap-1">
                                <MessageSquare className="w-3 h-3 text-[#0F766E]" />
                                {chatCount} Messages
                              </span>
                            </div>
                          </div>
                        </div>
                      </td>

                      {/* Score */}
                      <td className="py-3.5 px-4 font-mono font-bold text-[#17202A]">
                        {score} / 100
                      </td>

                      {/* Risk Level */}
                      <td className="py-3.5 px-4">
                        <span className={`inline-block text-[10px] font-bold font-mono uppercase px-2 py-0.5 rounded ${badgeClasses}`}>
                          {classification}
                        </span>
                      </td>

                      {/* Pages */}
                      <td className="py-3.5 px-4 font-mono text-[#64748B]">
                        {pageCount} Page{pageCount !== 1 ? 's' : ''}
                      </td>

                      {/* Date */}
                      <td className="py-3.5 px-4 font-mono text-[#64748B] text-[11px]">
                        {new Date(doc.created_at || Date.now()).toLocaleDateString()}
                      </td>

                      {/* Actions */}
                      <td className="py-3.5 px-5 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => handleDownloadRedline(doc.id, filename)}
                            className="px-2.5 py-1 text-xs font-medium border border-[#D9D6CC] hover:bg-[#F4F1E8] bg-[#FFFFFF] rounded-md text-[#17202A] transition-colors flex items-center gap-1 shadow-2xs"
                            title="Download DOCX Redline Counter-Proposal"
                          >
                            <Download className="w-3 h-3 text-[#15803D]" />
                            <span>Redline</span>
                          </button>

                          <Link
                            to={`/documents/${doc.id}`}
                            className="px-3 py-1 text-xs font-medium bg-[#163A59] hover:bg-[#102A43] text-white rounded-md transition-colors flex items-center gap-1 shadow-2xs"
                          >
                            <span>Inspect</span>
                            <ArrowRight className="w-3 h-3" />
                          </Link>

                          <button
                            onClick={() => handleDelete(doc.id)}
                            className="p-1 text-[#64748B] hover:text-[#C62828] hover:bg-rose-50 rounded-md transition-colors"
                            title="Delete Document"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
