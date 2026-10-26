import React, { useState, useEffect } from 'react';
import { templateAPI } from '../services/api';
import { Edit3, FileText, CheckCircle, AlertTriangle, Loader2 } from 'lucide-react';

const DEFAULT_TEMPLATES_FALLBACK = [
  {
    id: "nda-mutual",
    title: "Mutual Non-Disclosure Agreement (NDA)",
    category: "CONFIDENTIALITY",
    description: "Bilateral NDA protecting proprietary technical, financial, and business data.",
    form_schema: [
      { name: "party_a_name", label: "Disclosing Party A Name", type: "text", required: true, default: "Alpha Corp Pvt Ltd" },
      { name: "party_b_name", label: "Receiving Party B Name", type: "text", required: true, default: "Beta Solutions Inc" },
      { name: "effective_date", label: "Effective Date", type: "date", required: true, default: "2026-08-29" },
      { name: "governing_law", label: "Governing Jurisdiction", type: "text", required: true, default: "Laws of India / State of Maharashtra" },
      { name: "duration_months", label: "Confidentiality Term (Months)", type: "number", required: true, default: 24 }
    ]
  },
  {
    id: "master-services",
    title: "Master Services Agreement (MSA)",
    category: "SERVICES",
    description: "Standard commercial agreement for software development and IT consulting services.",
    form_schema: [
      { name: "party_a_name", label: "Client Name", type: "text", required: true, default: "Client Global Inc" },
      { name: "party_b_name", label: "Service Provider Name", type: "text", required: true, default: "LegalFlow Tech Ltd" },
      { name: "effective_date", label: "Agreement Date", type: "date", required: true, default: "2026-08-29" },
      { name: "payment_terms", label: "Payment Structure", type: "text", required: true, default: "Net 30 days upon monthly invoice" },
      { name: "governing_law", label: "Jurisdiction", type: "text", required: true, default: "Laws of India" }
    ]
  },
  {
    id: "commercial-lease",
    title: "Commercial Lease & Property Agreement",
    category: "REAL_ESTATE",
    description: "Lease agreement for commercial office space and retail premises.",
    form_schema: [
      { name: "party_a_name", label: "Lessor / Landlord", type: "text", required: true, default: "Prime Real Estate Ltd" },
      { name: "party_b_name", label: "Lessee / Tenant", type: "text", required: true, default: "Saurav Enterprises" },
      { name: "effective_date", label: "Lease Start Date", type: "date", required: true, default: "2026-09-01" },
      { name: "payment_terms", label: "Monthly Rent Amount (INR)", type: "text", required: true, default: "INR 85,000 per month" }
    ]
  }
];

export const Templates = () => {
  const [templates, setTemplates] = useState(DEFAULT_TEMPLATES_FALLBACK);
  const [selectedTemplate, setSelectedTemplate] = useState(DEFAULT_TEMPLATES_FALLBACK[0]);
  const [formData, setFormData] = useState({});
  const [title, setTitle] = useState('');
  const [generating, setGenerating] = useState(false);
  const [generatedDoc, setGeneratedDoc] = useState(null);

  useEffect(() => {
    selectTemplate(DEFAULT_TEMPLATES_FALLBACK[0]);
    if (templateAPI && typeof templateAPI.list === 'function') {
      templateAPI.list()
        .then(res => {
          if (res && Array.isArray(res.data) && res.data.length > 0) {
            setTemplates(res.data);
            selectTemplate(res.data[0]);
          }
        })
        .catch(() => {});
    }
  }, []);

  const selectTemplate = (tpl) => {
    if (!tpl) return;
    setSelectedTemplate(tpl);
    setTitle(tpl.title || '');
    setGeneratedDoc(null);

    const initial = {};
    if (tpl.form_schema) {
      tpl.form_schema.forEach(field => {
        initial[field.name] = field.default || '';
      });
    }
    setFormData(initial);
  };

  const handleInputChange = (name, value) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!selectedTemplate || generating) return;

    setGenerating(true);
    try {
      const payload = {
        template_id: selectedTemplate.id || 'nda-mutual',
        template_type: selectedTemplate.category || 'AGREEMENT',
        title: title || selectedTemplate.title || 'Contract',
        party_a_name: formData.party_a_name || formData.disclosing_party || formData.landlord_name || formData.client_name || 'Party A',
        party_b_name: formData.party_b_name || formData.receiving_party || formData.tenant_name || formData.freelancer_name || 'Party B',
        effective_date: formData.effective_date || formData.lease_start || formData.agreement_date || '2026-08-29',
        governing_law: formData.governing_law || formData.jurisdiction || 'Laws of India',
        payment_terms: formData.payment_terms || formData.payment_amount || formData.monthly_rent || 'Net 30',
        duration_months: parseInt(formData.duration_months || formData.term_months || 24),
        form_data: formData
      };

      const res = await templateAPI.generate(payload);
      
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      const downloadFilename = `Generated_${(selectedTemplate.title || 'Contract').replace(/[^a-zA-Z0-9]/g, '_')}.docx`;
      link.setAttribute('download', downloadFilename);
      document.body.appendChild(link);
      link.click();
      link.remove();

      setGeneratedDoc({ title: downloadFilename });
    } catch (err) {
      alert('Contract generation failed. Ensure backend server is active.');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <div className="mb-8">
        <h1 className="text-xl font-bold text-[#17202A] flex items-center gap-2.5 tracking-tight">
          <Edit3 className="w-5 h-5 text-[#0F766E]" />
          Contract Drafting & Template Generator
        </h1>
        <p className="text-xs text-[#64748B] mt-1">Generate balanced legal agreements customized to your exact requirements.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Templates Selector List */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold text-[#64748B] uppercase tracking-wider mb-2">Select Agreement Template</h3>
          {templates.map(tpl => (
            <div
              key={tpl.id}
              onClick={() => selectTemplate(tpl)}
              className={`p-4 rounded-lg border transition-all cursor-pointer shadow-2xs ${
                selectedTemplate?.id === tpl.id
                  ? 'bg-white border-2 border-[#163A59] text-[#17202A] shadow-xs'
                  : 'bg-white/90 border-[#D9D6CC] text-[#17202A] hover:bg-[#EAE6DC]/40'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-bold text-[#17202A]">{tpl.title}</span>
                <span className="text-[10px] bg-[#EAE6DC] text-[#17202A] border border-[#D9D6CC] px-2 py-0.5 rounded font-mono font-bold">{tpl.category}</span>
              </div>
              <p className="text-xs text-[#64748B] leading-relaxed mt-1">{tpl.description}</p>
            </div>
          ))}
        </div>

        {/* Dynamic Form View */}
        <div className="lg:col-span-2 bg-white border border-[#D9D6CC] p-6 rounded-lg shadow-2xs">
          {selectedTemplate ? (
            <form onSubmit={handleGenerate} className="space-y-5">
              <div className="border-b border-[#D9D6CC] pb-4">
                <h3 className="text-base font-bold text-[#17202A] tracking-tight">Fill Contract Details: {selectedTemplate.title}</h3>
                <p className="text-xs text-[#64748B] mt-0.5">All fields will be compiled into a formatted DOCX agreement.</p>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#17202A] mb-1">Agreement Document Title</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full bg-[#F4F1E8]/40 border border-[#D9D6CC] rounded-lg py-2 px-3 text-xs text-[#17202A] font-medium focus:border-[#163A59] focus:outline-none transition-colors"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {selectedTemplate.form_schema?.map(field => (
                  <div key={field.name} className={field.type === 'textarea' ? 'md:col-span-2' : ''}>
                    <label className="block text-xs font-semibold text-[#17202A] mb-1">{field.label}</label>
                    {field.type === 'textarea' ? (
                      <textarea
                        required={field.required}
                        rows={3}
                        value={formData[field.name] || ''}
                        onChange={(e) => handleInputChange(field.name, e.target.value)}
                        className="w-full bg-[#F4F1E8]/40 border border-[#D9D6CC] rounded-lg py-2 px-3 text-xs text-[#17202A] font-medium focus:border-[#163A59] focus:outline-none transition-colors"
                      />
                    ) : (
                      <input
                        type={field.type}
                        required={field.required}
                        value={formData[field.name] || ''}
                        onChange={(e) => handleInputChange(field.name, e.target.value)}
                        className="w-full bg-[#F4F1E8]/40 border border-[#D9D6CC] rounded-lg py-2 px-3 text-xs text-[#17202A] font-medium focus:border-[#163A59] focus:outline-none transition-colors"
                      />
                    )}
                  </div>
                ))}
              </div>

              <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-[11px] text-[#D97706] font-semibold flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0 text-[#D97706]" />
                <span>⚠️ AI-GENERATED DRAFT — REVIEW BY A QUALIFIED LEGAL PROFESSIONAL BEFORE SIGNING.</span>
              </div>

              <button
                type="submit"
                disabled={generating}
                className="w-full py-3 bg-[#163A59] hover:bg-[#102A43] disabled:opacity-50 text-white font-semibold text-xs rounded-lg shadow-2xs transition-colors flex items-center justify-center gap-2"
              >
                {generating ? <Loader2 className="w-4 h-4 animate-spin text-white" /> : <FileText className="w-4 h-4 text-white" />}
                {generating ? 'Drafting Contract...' : 'Generate & Download Custom DOCX Contract'}
              </button>

              {generatedDoc && (
                <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-lg flex items-center justify-between mt-4">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-[#15803D]" />
                    <div>
                      <span className="text-xs font-bold text-[#17202A]">Draft Generated & Downloaded Successfully!</span>
                      <p className="text-[11px] text-[#15803D] font-mono font-semibold">{generatedDoc.title}</p>
                    </div>
                  </div>
                </div>
              )}
            </form>
          ) : (
            <p className="text-xs text-[#64748B]">Select a template on the left.</p>
          )}
        </div>
      </div>
    </div>
  );
};
