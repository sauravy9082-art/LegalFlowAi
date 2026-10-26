import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Shield, Lock, LogOut, UploadCloud, LayoutDashboard, Edit3, GitCompare } from 'lucide-react';

export const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const isActive = (path) => 
    location.pathname === path 
      ? 'bg-[#FFFFFF] text-[#17202A] border border-[#D9D6CC] font-semibold shadow-2xs' 
      : 'text-slate-300 hover:text-white hover:bg-[#163A59] transition-colors font-medium';

  return (
    <nav className="h-14 border-b border-[#D9D6CC] bg-[#102A43] sticky top-0 z-50 px-6 flex items-center justify-between shadow-2xs">
      {/* Brand Logo */}
      <Link to="/" className="flex items-center gap-2.5 group">
        <div className="p-1.5 bg-[#B58B45] text-white rounded-md group-hover:bg-[#9E783A] transition-colors shadow-2xs">
          <Shield className="w-4 h-4 text-white" />
        </div>
        <div className="flex flex-col">
          <div className="flex items-center gap-1.5">
            <span className="text-sm font-bold text-white tracking-tight">LegalFlow AI</span>
            <span className="text-[9px] font-semibold uppercase tracking-wider px-1.5 py-0.2 bg-[#163A59] text-[#B58B45] border border-[#B58B45]/40 rounded">Enterprise</span>
          </div>
          <span className="text-[9px] text-slate-300 font-semibold uppercase tracking-wider">Automated Risk & Redline Studio</span>
        </div>
      </Link>

      {/* Center Nav Items */}
      {user && (
        <div className="flex items-center gap-1">
          <Link to="/dashboard" className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs transition ${isActive('/dashboard')}`}>
            <LayoutDashboard className="w-3.5 h-3.5 text-[#0F766E]" />
            <span>Dashboard</span>
          </Link>

          <Link to="/upload" className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs transition ${isActive('/upload')}`}>
            <UploadCloud className="w-3.5 h-3.5 text-[#0F766E]" />
            <span>Upload Contract</span>
          </Link>

          <Link to="/templates" className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs transition ${isActive('/templates')}`}>
            <Edit3 className="w-3.5 h-3.5 text-[#0F766E]" />
            <span>Draft Generator</span>
          </Link>

          <Link to="/compare" className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs transition ${isActive('/compare')}`}>
            <GitCompare className="w-3.5 h-3.5 text-[#0F766E]" />
            <span>Compare Contracts</span>
          </Link>

          <Link to="/privacy" className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs transition ${isActive('/privacy')}`}>
            <Lock className="w-3.5 h-3.5 text-[#15803D]" />
            <span>Privacy Center</span>
          </Link>
        </div>
      )}

      {/* Right User Actions */}
      <div className="flex items-center gap-3">
        {user ? (
          <div className="flex items-center gap-3 pl-4 border-l border-[#163A59]">
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-[#15803D]"></span>
              <span className="text-xs text-slate-200 font-semibold">{user.full_name || user.email}</span>
            </div>
            <button
              onClick={() => { logout(); navigate('/login'); }}
              className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-[#163A59] rounded-md transition-colors"
              title="Logout"
            >
              <LogOut className="w-3.5 h-3.5" />
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <Link
              to="/login"
              className="px-3.5 py-1.5 text-xs font-semibold text-slate-300 hover:text-white transition-colors"
            >
              Sign In
            </Link>
            <Link
              to="/register"
              className="px-3.5 py-1.5 text-xs font-semibold bg-[#B58B45] hover:bg-[#9E783A] text-white rounded-md transition-colors shadow-2xs"
            >
              Register
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
};
