import React, { useState, useEffect, useRef } from 'react';
import {
  FileText,
  ChevronLeft,
  ChevronRight,
  ShieldAlert,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Minimize2,
  RotateCcw,
  Layers
} from 'lucide-react';

export const PDFViewer = ({ document, pages = [], selectedFinding }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [viewMode, setViewMode] = useState('fit-width'); // 'fit-width' | 'fit-page'
  const [continuousScroll, setContinuousScroll] = useState(false);
  const [zoom, setZoom] = useState(100);
  const [containerSize, setContainerSize] = useState({ width: 800, height: 600 });

  const containerRef = useRef(null);
  const pageRefs = useRef({});

  // Measure container size dynamically
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const updateSize = () => {
      setContainerSize({
        width: el.clientWidth || 800,
        height: el.clientHeight || 600,
      });
    };

    updateSize();
    const observer = new ResizeObserver(updateSize);
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  // Jump to page when a finding is selected in the sidebar
  useEffect(() => {
    const findingPage = selectedFinding?.clause?.page_number || selectedFinding?.page_number || selectedFinding?.page;
    if (findingPage && findingPage >= 1) {
      setCurrentPage(findingPage);
      if (continuousScroll && pageRefs.current[findingPage]) {
        pageRefs.current[findingPage].scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  }, [selectedFinding, continuousScroll]);

  if (!document) {
    return (
      <div className="flex-1 flex items-center justify-center bg-[#F4F1E8] text-[#64748B] p-8">
        <p className="text-xs font-semibold text-[#64748B]">Select or upload a document to view.</p>
      </div>
    );
  }

  const safePages = Array.isArray(pages) && pages.length > 0 ? pages : [
    { page_number: 1, text_content: 'No text extracted for this document.' }
  ];
  const totalPages = safePages.length;

  const normalize = text => (text || '').replace(/\s+/g, ' ').trim().toLowerCase();
  const findingClauseText = selectedFinding?.clause?.original_text || selectedFinding?.original_text || selectedFinding?.evidence || '';
  const findingPageNumber = selectedFinding?.clause?.page_number || selectedFinding?.page_number || selectedFinding?.page;
  const normFindingText = normalize(findingClauseText);

  // Parse raw text into structured legal sections, preserving headings, breaks, and signatures
  const parseDocumentContent = (rawText) => {
    if (!rawText) return [];
    const text = rawText.replace(/\r\n/g, '\n').replace(/\r/g, '\n');

    // Split on double newlines OR legal section boundaries
    const sectionSplitRegex = /(?:\n\s*\n+)|(?=\n(?:\s*(?:[0-9]+[\.\)]\s+[A-Z]|Section\s+[0-9]+|Article\s+[IVX0-9]+|AUTHORIZED SIGNAT|IN WITNESS WHEREOF|PARTY [AB]:|Effective Date:)))/i;
    const rawBlocks = text.split(sectionSplitRegex);
    const blocks = [];

    for (const block of rawBlocks) {
      const trimmed = block.trim();
      if (!trimmed) continue;

      // Check if block starts with a clause heading like "1. Scope of Services" or "Section 2: Fees"
      const headingMatch = trimmed.match(/^((?:[0-9]+[\.\)]\s+[^:\n]+|Section\s+[0-9]+[^:\n]*|Article\s+[IVX0-9]+[^:\n]*))(?:\n+|:\s*)([\s\S]*)$/i);

      if (headingMatch && headingMatch[1].length < 80) {
        blocks.push({
          type: 'clause',
          heading: headingMatch[1].trim(),
          content: headingMatch[2].trim(),
          fullText: trimmed,
        });
      } else if (/^AUTHORIZED SIGNATORY|^IN WITNESS WHEREOF|^SIGNATURES/i.test(trimmed)) {
        blocks.push({
          type: 'signature',
          content: trimmed,
          fullText: trimmed,
        });
      } else if (/^Effective Date:|^Version Status:|^Disclosing|^Receiving/i.test(trimmed)) {
        blocks.push({
          type: 'metadata',
          content: trimmed,
          fullText: trimmed,
        });
      } else if (/^[A-Z0-9\s—–\-_,\.()]{8,}$/.test(trimmed.split('\n')[0]) && trimmed.split('\n').length <= 3) {
        blocks.push({
          type: 'title',
          content: trimmed,
          fullText: trimmed,
        });
      } else {
        blocks.push({
          type: 'paragraph',
          content: trimmed,
          fullText: trimmed,
        });
      }
    }

    return blocks;
  };

  // Track page while scrolling in continuous mode
  const handleScroll = () => {
    if (!continuousScroll || !containerRef.current) return;
    const containerTop = containerRef.current.getBoundingClientRect().top;

    for (let pNum = 1; pNum <= totalPages; pNum++) {
      const el = pageRefs.current[pNum];
      if (el) {
        const rect = el.getBoundingClientRect();
        if (rect.top <= containerTop + 200 && rect.bottom >= containerTop + 50) {
          setCurrentPage(pNum);
          break;
        }
      }
    }
  };

  const handlePageChange = (newPage) => {
    const target = Math.max(1, Math.min(totalPages, newPage));
    setCurrentPage(target);
    if (continuousScroll && pageRefs.current[target]) {
      pageRefs.current[target].scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else if (containerRef.current) {
      containerRef.current.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleZoomIn = () => setZoom(prev => Math.min(180, prev + 15));
  const handleZoomOut = () => setZoom(prev => Math.max(50, prev - 15));
  const handleResetZoom = () => setZoom(100);

  // Standard US Letter aspect ratio: 8.5 / 11 = 0.7727
  const BASE_WIDTH = 760;
  const BASE_RATIO = 8.5 / 11;
  const BASE_HEIGHT = Math.round(BASE_WIDTH / BASE_RATIO); // ~984px

  const availWidth = Math.max(280, containerSize.width - 48);
  const availHeight = Math.max(340, containerSize.height - 48);

  // Fit to Page scaling
  const fitPageScale = Math.min(availWidth / BASE_WIDTH, availHeight / BASE_HEIGHT) * (zoom / 100);

  // Fit to Width sizing
  const fitWidthPx = Math.min(availWidth, 860) * (zoom / 100);

  // Render formatted legal blocks
  const renderBlock = (block, idx, isClauseInThisPage) => {
    const normContent = normalize(block.content || block.fullText);
    const isMatch = Boolean(
      isClauseInThisPage &&
      normFindingText &&
      normContent &&
      (normContent.includes(normFindingText) || normFindingText.includes(normContent))
    );

    const highlightClass = isMatch
      ? 'bg-rose-50 border-l-4 border-rose-500 pl-3 py-1.5 rounded-r shadow-xs text-[#17202A] font-medium'
      : '';

    if (block.type === 'title') {
      return (
        <div key={idx} className={`text-center my-3 pb-2 border-b border-[#D9D6CC] ${highlightClass}`}>
          <h2 className="text-xs sm:text-sm font-bold text-[#102A43] tracking-wide uppercase">
            {block.content}
          </h2>
        </div>
      );
    }

    if (block.type === 'metadata') {
      return (
        <div key={idx} className={`p-3 bg-[#F4F1E8]/70 border border-[#D9D6CC] rounded text-[10px] sm:text-[11px] font-mono text-[#475569] space-y-1 my-3 ${highlightClass}`}>
          <div className="whitespace-pre-line leading-relaxed">
            {block.content}
          </div>
        </div>
      );
    }

    if (block.type === 'clause') {
      return (
        <div key={idx} className={`my-3 sm:my-4 ${highlightClass}`}>
          <div className="font-bold text-[#163A59] text-[11px] sm:text-xs border-b border-[#D9D6CC]/60 pb-1 mb-1.5 flex items-center gap-1.5 tracking-tight">
            <span className="w-1.5 h-1.5 rounded-full bg-[#B58B45]"></span>
            <span>{block.heading}</span>
          </div>
          <div className="text-[10px] sm:text-[11px] font-sans leading-relaxed text-[#17202A] whitespace-pre-line pl-1.5">
            {block.content}
          </div>
        </div>
      );
    }

    if (block.type === 'signature') {
      return (
        <div key={idx} className={`pt-4 border-t-2 border-dashed border-[#D9D6CC] mt-6 mb-2 ${highlightClass}`}>
          <div className="text-[10px] sm:text-[11px] font-mono text-[#475569] whitespace-pre-line leading-relaxed">
            {block.content}
          </div>
        </div>
      );
    }

    // Standard paragraph
    return (
      <div key={idx} className={`my-2 text-[10px] sm:text-[11px] font-sans leading-relaxed text-[#17202A] whitespace-pre-line ${highlightClass}`}>
        {block.content}
      </div>
    );
  };

  // Render a single page sheet
  const renderPageSheet = (pageData) => {
    const pageNum = pageData.page_number || 1;
    const rawText = pageData.text_content || pageData.text || pageData.extracted_text || 'No text extracted for this page.';
    const blocks = parseDocumentContent(rawText);
    const isClauseInThisPage = Boolean(
      selectedFinding &&
      findingClauseText &&
      (findingPageNumber === pageNum || (!findingPageNumber && totalPages === 1))
    );

    if (viewMode === 'fit-page') {
      return (
        <div
          key={pageNum}
          ref={el => pageRefs.current[pageNum] = el}
          style={{
            width: `${BASE_WIDTH * fitPageScale}px`,
            height: `${BASE_HEIGHT * fitPageScale}px`,
            margin: 'auto',
          }}
          className="relative shrink-0 select-text"
        >
          {/* Scaled paper sheet */}
          <div
            style={{
              width: `${BASE_WIDTH}px`,
              height: `${BASE_HEIGHT}px`,
              transform: `scale(${fitPageScale})`,
              transformOrigin: 'top left',
            }}
            className="bg-white border border-[#D9D6CC] shadow-lg rounded-sm p-8 flex flex-col justify-between overflow-hidden"
          >
            {/* Sheet Header */}
            <div>
              <div className="flex items-center justify-between pb-2.5 border-b border-[#D9D6CC] mb-4 text-[10px] text-[#64748B] font-mono">
                <span className="font-semibold uppercase tracking-wider truncate max-w-[450px]">
                  {document.original_filename || document.filename}
                </span>
                <span className="font-bold">PAGE {pageNum} OF {totalPages}</span>
              </div>

              {/* Active Risk Highlight Banner */}
              {isClauseInThisPage && (
                <div className="mb-4 p-2.5 rounded border-l-4 border-[#C62828] bg-rose-50 border border-rose-200 text-[#C62828] text-[11px] shadow-2xs">
                  <div className="flex items-center gap-1.5 font-bold mb-0.5 uppercase tracking-wider text-[9px]">
                    <ShieldAlert className="w-3.5 h-3.5" />
                    <span>Active Risk: {selectedFinding?.category || 'Risk Clause'}</span>
                  </div>
                  <p className="font-mono text-[10px] leading-relaxed truncate">"{findingClauseText}"</p>
                </div>
              )}

              {/* Structured Blocks with Clean Spacing & Headings */}
              <div className="overflow-y-auto max-h-[780px] pr-2">
                {blocks.map((block, idx) => renderBlock(block, idx, isClauseInThisPage))}
              </div>
            </div>

            {/* Sheet Footer */}
            <div className="pt-3 border-t border-[#D9D6CC] text-[9px] text-[#64748B] text-center font-mono">
              LegalFlow AI Inspection Canvas • Page {pageNum} of {totalPages}
            </div>
          </div>
        </div>
      );
    }

    // Default: 'fit-width' mode
    return (
      <div
        key={pageNum}
        ref={el => pageRefs.current[pageNum] = el}
        style={{
          width: `${fitWidthPx}px`,
          minHeight: `${fitWidthPx / BASE_RATIO}px`,
        }}
        className="bg-white border border-[#D9D6CC] shadow-lg rounded-sm p-6 sm:p-10 my-4 flex flex-col justify-between relative transition-all"
      >
        {/* Sheet Header */}
        <div>
          <div className="flex items-center justify-between pb-3 border-b border-[#D9D6CC] mb-6 text-[10px] text-[#64748B] font-mono">
            <span className="font-semibold uppercase tracking-wider truncate max-w-[450px]">
              {document.original_filename || document.filename}
            </span>
            <span className="font-bold">PAGE {pageNum} OF {totalPages}</span>
          </div>

          {/* Active Risk Highlight Banner */}
          {isClauseInThisPage && (
            <div className="mb-5 p-3 rounded-lg border-l-4 border-[#C62828] bg-rose-50 border border-rose-200 text-[#C62828] text-xs shadow-2xs">
              <div className="flex items-center gap-2 font-bold mb-1 uppercase tracking-wider text-[10px]">
                <ShieldAlert className="w-3.5 h-3.5 text-[#C62828]" />
                <span>Active Risk Highlight: {selectedFinding?.category || 'Risk Clause'}</span>
              </div>
              <p className="font-mono text-[11px] leading-relaxed">"{findingClauseText}"</p>
            </div>
          )}

          {/* Structured Blocks with Clean Spacing & Headings */}
          <div className="space-y-1">
            {blocks.map((block, idx) => renderBlock(block, idx, isClauseInThisPage))}
          </div>
        </div>

        {/* Sheet Footer */}
        <div className="pt-4 border-t border-[#D9D6CC] mt-8 text-[10px] text-[#64748B] text-center font-mono">
          LegalFlow AI — Confidential & Private Local Document Inspection • Page {pageNum} of {totalPages}
        </div>
      </div>
    );
  };

  const pagesToRender = continuousScroll
    ? safePages
    : [safePages.find(p => p.page_number === currentPage) || safePages[0]];

  return (
    <div className="flex-1 flex flex-col h-full bg-[#EAE6DC] text-[#17202A] overflow-hidden">
      {/* Top Utility Toolbar */}
      <div className="h-10 px-3 md:px-4 bg-[#102A43] border-b border-[#D9D6CC] flex items-center justify-between z-10 shrink-0 shadow-2xs gap-2">
        {/* Left: Document Info */}
        <div className="flex items-center gap-2 min-w-0">
          <FileText className="w-3.5 h-3.5 text-[#B58B45] shrink-0" />
          <span className="text-xs font-semibold text-white truncate max-w-[140px] sm:max-w-xs" title={document.original_filename || document.filename}>
            {document.original_filename || document.filename}
          </span>
          <span className="text-[9px] bg-[#163A59] border border-amber-500/30 text-amber-200 px-1.5 py-0.2 rounded font-mono uppercase font-bold shrink-0">
            {document.file_type || 'PDF'}
          </span>
          {document.is_scanned && (
            <span className="text-[9px] bg-amber-500/20 text-amber-300 border border-amber-400/40 px-1.5 py-0.2 rounded font-mono font-bold shrink-0 hidden sm:inline">
              OCR
            </span>
          )}
        </div>

        {/* Center: View Mode & Zoom Controls */}
        <div className="flex items-center gap-1 shrink-0">
          {/* Fit to Width Button */}
          <button
            onClick={() => {
              setViewMode('fit-width');
              setZoom(100);
            }}
            className={`flex items-center gap-1 px-2 py-1 rounded text-[11px] font-medium transition-colors ${
              viewMode === 'fit-width'
                ? 'bg-[#163A59] text-white border border-slate-500'
                : 'text-slate-300 hover:text-white hover:bg-[#163A59]/60'
            }`}
            title="Fit to Width (Comfortable Reading & Vertical Scroll)"
          >
            <Maximize2 className="w-3 h-3" />
            <span className="hidden md:inline">Fit Width</span>
          </button>

          {/* Fit to Page Button */}
          <button
            onClick={() => {
              setViewMode('fit-page');
              setZoom(100);
            }}
            className={`flex items-center gap-1 px-2 py-1 rounded text-[11px] font-medium transition-colors ${
              viewMode === 'fit-page'
                ? 'bg-[#163A59] text-white border border-slate-500'
                : 'text-slate-300 hover:text-white hover:bg-[#163A59]/60'
            }`}
            title="Fit to Page (Complete Aspect-Ratio Page in View)"
          >
            <Minimize2 className="w-3 h-3" />
            <span className="hidden md:inline">Fit Page</span>
          </button>

          <div className="h-4 w-[1px] bg-slate-700 mx-1 hidden sm:block"></div>

          {/* Zoom Out */}
          <button
            onClick={handleZoomOut}
            disabled={zoom <= 50}
            className="p-1 rounded text-slate-300 hover:text-white hover:bg-[#163A59] disabled:opacity-30 transition-colors"
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>

          {/* Zoom Level Indicator / Reset */}
          <button
            onClick={handleResetZoom}
            className="text-[10px] font-mono font-bold text-slate-200 px-1 py-0.5 hover:text-white hover:bg-[#163A59] rounded"
            title="Reset Zoom to 100%"
          >
            {zoom}%
          </button>

          {/* Zoom In */}
          <button
            onClick={handleZoomIn}
            disabled={zoom >= 180}
            className="p-1 rounded text-slate-300 hover:text-white hover:bg-[#163A59] disabled:opacity-30 transition-colors"
            title="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>

          {/* Multi-Page Continuous Scroll Toggle */}
          {totalPages > 1 && (
            <>
              <div className="h-4 w-[1px] bg-slate-700 mx-1 hidden sm:block"></div>
              <button
                onClick={() => setContinuousScroll(!continuousScroll)}
                className={`flex items-center gap-1 px-2 py-1 rounded text-[11px] font-medium transition-colors ${
                  continuousScroll
                    ? 'bg-[#B58B45] text-white'
                    : 'text-slate-300 hover:text-white hover:bg-[#163A59]/60'
                }`}
                title={continuousScroll ? 'Continuous Scroll Active' : 'Switch to Continuous Scroll for Multi-Page'}
              >
                <Layers className="w-3 h-3" />
                <span className="hidden lg:inline">{continuousScroll ? 'All Pages' : 'Single'}</span>
              </button>
            </>
          )}
        </div>

        {/* Right: Page Navigation */}
        <div className="flex items-center gap-1 sm:gap-2 shrink-0">
          <button
            disabled={currentPage <= 1}
            onClick={() => handlePageChange(currentPage - 1)}
            className="p-1 rounded text-slate-300 hover:text-white disabled:opacity-30 hover:bg-[#163A59] transition-colors"
            title="Previous Page"
          >
            <ChevronLeft className="w-3.5 h-3.5" />
          </button>
          <span className="text-[11px] font-mono font-bold text-slate-200 whitespace-nowrap">
            {currentPage} / {totalPages}
          </span>
          <button
            disabled={currentPage >= totalPages}
            onClick={() => handlePageChange(currentPage + 1)}
            className="p-1 rounded text-slate-300 hover:text-white disabled:opacity-30 hover:bg-[#163A59] transition-colors"
            title="Next Page"
          >
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Main Canvas Area */}
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-auto p-4 sm:p-6 flex flex-col items-center bg-[#E5E2D9] relative select-text"
      >
        <div className="min-h-full flex flex-col items-center justify-center my-auto w-full">
          {pagesToRender.map(pageData => renderPageSheet(pageData))}
        </div>
      </div>
    </div>
  );
};
