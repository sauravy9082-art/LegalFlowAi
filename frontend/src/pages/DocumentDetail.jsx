import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { documentAPI, redlineAPI } from '../services/api';
import { PDFViewer } from '../components/PDFViewer';
import { RiskSidebar } from '../components/RiskSidebar';
import { ChatPanel } from '../components/ChatPanel';
import { Shield, FileText, MessageSquare, AlertCircle, RefreshCw, ArrowLeft, UploadCloud } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const DocumentDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { loginAsGuest } = useAuth();
  const [doc, setDoc] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [selectedFinding, setSelectedFinding] = useState(null);
  const [activeTab, setActiveTab] = useState('risks');
  const [analyzing, setAnalyzing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    fetchDocData();
  }, [id]);

  const fetchDocData = async (retryWithGuest = true) => {
    setLoading(true);
    setErrorMsg('');
    try {
      const docRes = await documentAPI.getById(id);
      setDoc(docRes.data);
      setLoading(false);

      try {
        const analysisRes = await documentAPI.getAnalysis(id);
        setAnalysis(analysisRes.data);
        if (analysisRes.data && analysisRes.data.document && analysisRes.data.document.pages && analysisRes.data.document.pages.length > 0) {
          setDoc(analysisRes.data.document);
        }
      } catch (err) {
        setAnalyzing(true);
        try {
          const autoRes = await documentAPI.analyze(id);
          setAnalysis(autoRes.data);
          if (autoRes.data && autoRes.data.document) {
            setDoc(autoRes.data.document);
          }
        } catch (e) {
          setAnalysis(null);
        } finally {
          setAnalyzing(false);
        }
      }
    } catch (err) {
      setLoading(false);
      if (err.response?.status === 403 && retryWithGuest) {
        try {
          await loginAsGuest();
          return fetchDocData(false);
        } catch (guestErr) {
          setErrorMsg('Document access restricted. Please log in with the account that uploaded this contract.');
        }
      } else {
        setErrorMsg(err.response?.data?.detail || 'Failed to load document analysis details. Please verify backend connection.');
      }
    }
  };

  const handleRunAnalysis = async () => {
    setAnalyzing(true);
    try {
      const res = await documentAPI.analyze(id);
      setAnalysis(res.data);
      if (res.data && res.data.document) {
        setDoc(res.data.document);
      }
    } catch (err) {
      alert('Analysis failed. Ensure local Ollama service or rule engine is active.');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleGenerateRedline = async () => {
    try {
      const res = await redlineAPI.exportDocx(id);
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Redlined_${doc?.original_filename || 'Contract'}.docx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Failed to generate DOCX redline proposal.');
    }
  };

  if (loading) {
    return (
      <div className="min-h-[80vh] flex flex-col items-center justify-center p-12 text-[#64748B]">
        <RefreshCw className="w-6 h-6 animate-spin text-[#163A59] mb-3" />
        <span className="text-xs font-semibold text-[#17202A]">Loading contract inspection workspace...</span>
        <span className="text-[11px] text-[#64748B] mt-1 font-mono">Extracting pages, risks, and local AI recommendations</span>
      </div>
    );
  }

  if (errorMsg || !doc) {
    return (
      <div className="min-h-[80vh] flex flex-col items-center justify-center p-8 text-center">
        <div className="w-full max-w-md bg-[#FFFFFF] border border-[#D9D6CC] p-8 rounded-lg shadow-2xs">
          <div className="inline-flex p-2.5 rounded-lg bg-amber-50 border border-amber-200 text-[#D97706] mb-4">
            <AlertCircle className="w-6 h-6" />
          </div>
          <h3 className="text-base font-bold text-[#17202A] mb-2">Inspection Workspace Notice</h3>
          <p className="text-xs text-[#64748B] leading-relaxed mb-6">{errorMsg || 'Document not found.'}</p>
          <div className="flex gap-3">
            <button
              onClick={() => fetchDocData(true)}
              className="flex-1 py-2 bg-[#163A59] hover:bg-[#102A43] text-white text-xs font-semibold rounded-md transition-colors flex items-center justify-center gap-2 shadow-2xs"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Retry Load</span>
            </button>
            <Link
              to="/upload"
              className="flex-1 py-2 bg-white hover:bg-[#F4F1E8] text-[#17202A] text-xs font-semibold rounded-md border border-[#D9D6CC] transition-colors flex items-center justify-center gap-2 shadow-2xs"
            >
              <UploadCloud className="w-3.5 h-3.5 text-[#15803D]" />
              <span>Upload Contract</span>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[calc(100vh-56px)] bg-[#F4F1E8] overflow-hidden">
      {/* Top Utility Toolbar */}
      <div className="h-12 px-4 bg-[#102A43] border-b border-[#D9D6CC] flex items-center justify-between z-20 shrink-0 shadow-2xs">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/dashboard')}
            className="p-1 text-slate-300 hover:text-white hover:bg-[#163A59] rounded-md transition-colors"
            title="Back to Dashboard"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>

          <div className="p-1.5 rounded-md bg-[#B58B45] text-white shadow-2xs">
            <Shield className="w-4 h-4 text-white" />
          </div>
          <div>
            <h2 className="text-xs font-bold text-white flex items-center gap-2 tracking-tight">
              {doc.original_filename || doc.filename}
              <span className="text-[9px] bg-[#163A59] border border-amber-500/30 text-amber-200 px-1.5 py-0.2 rounded font-mono uppercase font-bold">
                {doc.mime_type?.includes('pdf') ? 'PDF' : doc.file_type || 'DOC'}
              </span>
            </h2>
            <p className="text-[10px] text-slate-300 font-mono">
              Status: {doc.status} • {doc.pages ? doc.pages.length : (doc.page_count || 1)} Pages • Air-Gapped Local Inspection
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleRunAnalysis}
            disabled={analyzing}
            className="flex items-center gap-2 px-3 py-1.5 bg-[#B58B45] hover:bg-[#9E783A] disabled:opacity-50 text-white font-semibold text-xs rounded-md shadow-2xs transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-white ${analyzing ? 'animate-spin' : ''}`} />
            {analyzing ? 'Analyzing with Ollama...' : 'Re-Run AI Analysis'}
          </button>
        </div>
      </div>

      {/* Main Workspace Split-Screen */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Pane: PDF Viewer */}
        <div className="flex-1 flex flex-col min-w-0">
          <PDFViewer
            document={doc}
            pages={doc.pages || []}
            selectedFinding={selectedFinding}
          />
        </div>

        {/* Right Pane: Risk Sidebar & Chat Panel */}
        <div className="w-[420px] flex flex-col border-l border-[#D9D6CC] bg-[#EAE6DC] shrink-0">
          {/* Tab Selection Bar */}
          <div className="h-10 p-1 border-b border-[#D9D6CC] bg-[#EAE6DC] flex gap-1 shrink-0">
            <button
              onClick={() => setActiveTab('risks')}
              className={`flex-1 text-xs font-semibold flex items-center justify-center gap-2 rounded-md transition-colors ${
                activeTab === 'risks'
                  ? 'bg-[#FFFFFF] text-[#17202A] border border-[#D9D6CC] shadow-2xs'
                  : 'text-[#64748B] hover:text-[#17202A] hover:bg-[#FFFFFF]/60'
              }`}
            >
              <Shield className="w-3.5 h-3.5 text-[#0F766E]" />
              <span>Risk Findings & Score</span>
            </button>
            <button
              onClick={() => setActiveTab('chat')}
              className={`flex-1 text-xs font-semibold flex items-center justify-center gap-2 rounded-md transition-colors ${
                activeTab === 'chat'
                  ? 'bg-[#FFFFFF] text-[#17202A] border border-[#D9D6CC] shadow-2xs'
                  : 'text-[#64748B] hover:text-[#17202A] hover:bg-[#FFFFFF]/60'
              }`}
            >
              <MessageSquare className="w-3.5 h-3.5 text-[#0F766E]" />
              <span>Legal AI Assistant</span>
            </button>
          </div>

          {/* Active Tab View */}
          <div className="flex-1 overflow-hidden">
            {activeTab === 'risks' ? (
              <RiskSidebar
                analysis={analysis}
                onSelectFinding={(f) => setSelectedFinding(f)}
                selectedFindingId={selectedFinding?.id}
                onGenerateRedline={handleGenerateRedline}
              />
            ) : (
              <ChatPanel documentId={doc.id} />
            )}
          </div>
        </div>
      </div>

      {/* Mandatory Disclaimer Footer */}
      <div className="py-1.5 px-4 bg-[#EAE6DC] border-t border-[#D9D6CC] text-[10px] text-[#64748B] text-center flex items-center justify-center gap-1.5 font-mono z-20 shrink-0">
        <AlertCircle className="w-3.5 h-3.5 text-[#D97706] shrink-0" />
        <span>LegalFlow AI is an informational document-analysis tool and does not replace a qualified lawyer or provide legal representation.</span>
      </div>
    </div>
  );
};
