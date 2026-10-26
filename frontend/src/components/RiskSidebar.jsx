import React, { useState } from 'react';
import { ShieldAlert, Globe, ChevronRight, FileText, ArrowRight, CheckCircle } from 'lucide-react';

export const RiskSidebar = ({ analysis, onSelectFinding, selectedFindingId, onGenerateRedline }) => {
  const [selectedLanguage, setSelectedLanguage] = useState('english');

  if (!analysis) {
    return (
      <div className="p-6 text-center text-[#64748B] bg-[#EAE6DC] h-full border-l border-[#D9D6CC]">
        <ShieldAlert className="w-10 h-10 mx-auto mb-3 text-[#0F766E]" />
        <p className="text-xs font-semibold text-[#17202A]">No analysis data available yet.</p>
        <p className="text-[11px] text-[#64748B] mt-1">Click "Re-Run AI Analysis" to extract risk findings and safety score.</p>
      </div>
    );
  }

  const safety_score = analysis.deterministic_risk_score ?? analysis.safety_score ?? 100;
  const risk_level = analysis.risk_classification ?? analysis.risk_level ?? 'GREEN';
  const risk_findings = analysis.clauses || analysis.risk_findings || [];
  const recommendations = analysis.recommendations || [];
  const summary = analysis.summary || '';

  const getScoreBadge = (score) => {
    if (score >= 85) {
      return {
        bg: 'bg-emerald-50 text-[#15803D] border border-emerald-200',
        ring: 'stroke-[#15803D]',
        english: 'SAFE / LOW CONCERN',
        hindi: 'सुरक्षित / कम जोखिम',
        marathi: 'सुरक्षित / कमी धोका'
      };
    }
    if (score >= 65) {
      return {
        bg: 'bg-yellow-50 text-[#CA8A04] border border-yellow-200',
        ring: 'stroke-[#CA8A04]',
        english: 'MODERATE WARNING',
        hindi: 'मध्यम चेतावनी',
        marathi: 'मध्यम इशारा'
      };
    }
    if (score >= 45) {
      return {
        bg: 'bg-amber-50 text-[#D97706] border border-amber-200',
        ring: 'stroke-[#D97706]',
        english: 'HIGH CONCERN',
        hindi: 'उच्च चिंताजनक जोखिम',
        marathi: 'उच्च चिंतेचा धोका'
      };
    }
    return {
      bg: 'bg-rose-50 text-[#C62828] border border-rose-200',
      ring: 'stroke-[#C62828]',
      english: 'CRITICAL RISK',
      hindi: 'गंभीर कानूनी जोखिम',
      marathi: 'गंभीर कायदेशीर धोका'
    };
  };

  const badge = getScoreBadge(safety_score);

  const getBadgeLabel = () => {
    if (selectedLanguage === 'hindi') return badge.hindi;
    if (selectedLanguage === 'marathi') return badge.marathi;
    return badge.english;
  };

  const getExplanation = (finding) => {
    if (!finding) return '';
    const multi = finding.multilingual_explanations || {};
    if (selectedLanguage === 'hindi') {
      return multi.hi || finding.explanation_hi || finding.explanation || finding.reason;
    }
    if (selectedLanguage === 'marathi') {
      return multi.mr || finding.explanation_mr || finding.explanation || finding.reason;
    }
    return finding.explanation || finding.reason || finding.summary || 'Clause parsed for legal risk.';
  };

  const getHeaderTitle = () => {
    if (selectedLanguage === 'hindi') return 'अनुबंध सुरक्षा स्कोर';
    if (selectedLanguage === 'marathi') return 'करार सुरक्षा स्कोर';
    return 'Contract Safety Score';
  };

  const getSummaryHeader = () => {
    if (selectedLanguage === 'hindi') return 'कार्यकारी सारांश';
    if (selectedLanguage === 'marathi') return 'कार्यकारी सारांश';
    return 'Executive Summary';
  };

  const getRecommendationsHeader = () => {
    if (selectedLanguage === 'hindi') return 'कानूनी सिफारिशें';
    if (selectedLanguage === 'marathi') return 'कायदेशीर शिफारसी';
    return 'Legal Recommendations';
  };

  const getFindingsHeader = () => {
    if (selectedLanguage === 'hindi') return 'पहचाने गए जोखिम और धाराएं';
    if (selectedLanguage === 'marathi') return 'ओळखलेले धोके आणि कलमे';
    return 'Identified Risk Findings';
  };

  const getRedlineButtonText = () => {
    if (selectedLanguage === 'hindi') return 'DOCX रेडलाइन काउंटर-प्रस्ताव तैयार करें';
    if (selectedLanguage === 'marathi') return 'DOCX रेडलाइन काउंटर-प्रस्ताव तयार करा';
    return 'Generate DOCX Redline Counter-Proposal';
  };

  return (
    <div className="flex flex-col h-full bg-[#EAE6DC] text-[#17202A] border-l border-[#D9D6CC] overflow-y-auto">
      {/* Score Header */}
      <div className="p-4 border-b border-[#D9D6CC] bg-[#102A43] text-white sticky top-0 z-10">
        <div className="flex items-center justify-between mb-3">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-200">{getHeaderTitle()}</span>
          
          {/* Language Selector */}
          <div className="flex items-center gap-0.5 bg-[#163A59] p-0.5 rounded-md border border-[#D9D6CC]/40 shadow-2xs">
            <Globe className="w-3 h-3 text-slate-300 ml-1" />
            <button
              onClick={() => setSelectedLanguage('english')}
              className={`px-1.5 py-0.5 text-[10px] font-bold rounded transition-colors ${selectedLanguage === 'english' ? 'bg-[#B58B45] text-white' : 'text-slate-300 hover:text-white'}`}
            >
              EN
            </button>
            <button
              onClick={() => setSelectedLanguage('hindi')}
              className={`px-1.5 py-0.5 text-[10px] font-bold rounded transition-colors ${selectedLanguage === 'hindi' ? 'bg-[#B58B45] text-white' : 'text-slate-300 hover:text-white'}`}
            >
              हिन्दी
            </button>
            <button
              onClick={() => setSelectedLanguage('marathi')}
              className={`px-1.5 py-0.5 text-[10px] font-bold rounded transition-colors ${selectedLanguage === 'marathi' ? 'bg-[#B58B45] text-white' : 'text-slate-300 hover:text-white'}`}
            >
              मराठी
            </button>
          </div>
        </div>

        <div className="flex items-center justify-between bg-[#FFFFFF] p-3.5 rounded-lg border border-[#D9D6CC] shadow-2xs text-[#17202A]">
          <div>
            <div className="text-2xl font-bold tracking-tight text-[#17202A] font-mono">{safety_score}<span className="text-xs text-[#64748B] font-normal">/100</span></div>
            <span className={`inline-block mt-1 px-2 py-0.5 text-[9px] font-bold uppercase rounded ${badge.bg}`}>
              {getBadgeLabel()}
            </span>
          </div>

          <div className="w-12 h-12 relative flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
              <path className="text-slate-200" strokeWidth="3" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
              <path className={badge.ring} strokeDasharray={`${safety_score}, 100`} strokeWidth="3" strokeLinecap="round" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
            </svg>
          </div>
        </div>

        {onGenerateRedline && (
          <button
            onClick={onGenerateRedline}
            className="w-full mt-3 flex items-center justify-center gap-2 py-2 px-3 bg-[#163A59] hover:bg-[#102A43] text-white font-semibold text-xs rounded-md shadow-2xs transition-colors"
          >
            <FileText className="w-3.5 h-3.5 text-white" />
            {getRedlineButtonText()}
          </button>
        )}
      </div>

      {/* Summary */}
      {summary && (
        <div className="p-4 border-b border-[#D9D6CC] bg-[#FFFFFF]">
          <h4 className="text-[10px] font-bold text-[#64748B] uppercase tracking-wider mb-1.5">{getSummaryHeader()}</h4>
          <p className="text-xs text-[#17202A] leading-relaxed">{summary}</p>
        </div>
      )}

      {/* AI Recommendations */}
      {recommendations.length > 0 && (
        <div className="p-4 border-b border-[#D9D6CC] bg-emerald-50/60">
          <h4 className="text-[10px] font-bold text-[#15803D] uppercase tracking-wider mb-2">{getRecommendationsHeader()}</h4>
          <ul className="space-y-1.5">
            {recommendations.map((rec, idx) => (
              <li key={idx} className="text-xs text-[#17202A] flex items-start gap-1.5 leading-snug">
                <CheckCircle className="w-3.5 h-3.5 text-[#15803D] shrink-0 mt-0.5" />
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Risk Findings List */}
      <div className="p-4 space-y-3 flex-1">
        <h4 className="text-[10px] font-bold text-[#64748B] uppercase tracking-wider flex items-center justify-between">
          <span>{getFindingsHeader()}</span>
          <span className="bg-[#FFFFFF] text-[#17202A] px-2 py-0.5 rounded text-[10px] font-mono border border-[#D9D6CC] font-bold">{risk_findings.length}</span>
        </h4>

        {risk_findings.length === 0 ? (
          <div className="p-4 rounded-md bg-emerald-50 border border-emerald-200 text-center">
            <CheckCircle className="w-6 h-6 text-[#15803D] mx-auto mb-1.5" />
            <p className="text-xs text-[#15803D] font-medium">
              {selectedLanguage === 'hindi' ? 'इस अनुबंध में कोई गंभीर कानूनी जोखिम नहीं मिला।' :
               selectedLanguage === 'marathi' ? 'या करारात कोणताही गंभीर कायदेशीर धोका आढळला नाही.' :
               'No critical legal risks detected in this agreement.'}
            </p>
          </div>
        ) : (
          risk_findings.map((finding, idx) => {
            const isSelected = selectedFindingId === (finding.id || idx);
            const rLevel = finding.risk_level || finding.category || 'LOW';

            let badgeStyle = 'bg-yellow-50 text-[#CA8A04] border border-yellow-200';
            if (rLevel === 'RED' || rLevel === 'CRITICAL') badgeStyle = 'bg-rose-50 text-[#C62828] border border-rose-200';
            else if (rLevel === 'ORANGE' || rLevel === 'HIGH') badgeStyle = 'bg-amber-50 text-[#D97706] border border-amber-200';

            return (
              <div
                key={finding.id || idx}
                onClick={() => onSelectFinding(finding)}
                className={`p-3.5 rounded-lg border transition-all cursor-pointer shadow-2xs ${
                  isSelected
                    ? 'bg-[#FFFFFF] border-[#163A59] ring-1 ring-[#163A59]'
                    : 'bg-[#FFFFFF] border-[#D9D6CC] hover:border-slate-400 hover:bg-[#F4F1E8]/50'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className={`text-[9px] font-bold uppercase px-2 py-0.5 rounded font-mono ${badgeStyle}`}>
                    {finding.category || 'Legal Clause'}
                  </span>

                  <span className="text-[10px] text-[#0F766E] font-medium flex items-center gap-0.5">
                    Inspect <ChevronRight className="w-3 h-3 text-[#0F766E]" />
                  </span>
                </div>

                {/* Clause Quote */}
                {(finding.clause || finding.original_text) && (
                  <div className="mb-2 p-2 bg-[#F4F1E8] rounded border border-[#D9D6CC] text-[11px] font-mono text-[#17202A] italic">
                    "{finding.clause?.original_text || finding.original_text}"
                  </div>
                )}

                {/* Language Explanation */}
                <p className="text-xs font-semibold text-[#17202A] mb-1.5 leading-relaxed">
                  {getExplanation(finding)}
                </p>

                {finding.suggested_action && (
                  <div className="mt-2 text-[11px] text-[#15803D] font-medium flex items-start gap-1">
                    <ArrowRight className="w-3 h-3 mt-0.5 shrink-0 text-[#15803D]" />
                    <span>{finding.suggested_action}</span>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
