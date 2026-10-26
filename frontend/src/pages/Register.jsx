import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Shield, Lock, Mail, User, Building2, AlertCircle, Eye, EyeOff } from 'lucide-react';

export const Register = () => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [organization, setOrganization] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { user, register } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      navigate('/dashboard', { replace: true });
    }
  }, [user, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Field validation
    const trimmedName = fullName.trim();
    if (!trimmedName) {
      setError('Please enter your full name.');
      return;
    }

    const trimmedEmail = email.trim();
    if (!trimmedEmail) {
      setError('Please enter your email address.');
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(trimmedEmail)) {
      setError('Invalid email format (e.g. user@legalflow.ai).');
      return;
    }

    if (!password) {
      setError('Please enter your password.');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }

    setLoading(true);
    try {
      await register(trimmedEmail, password, trimmedName, organization.trim());
      navigate('/dashboard');
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (typeof detail === 'string') {
        setError(detail);
      } else if (Array.isArray(detail)) {
        const emailErr = detail.find(d => d.loc && d.loc.includes('email'));
        if (emailErr) {
          setError('Invalid email format.');
        } else {
          setError(detail.map(d => d.msg || JSON.stringify(d)).join(' | '));
        }
      } else {
        setError('Registration failed. Please check details and try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-3.5rem)] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md bg-white border border-[#D9D6CC] p-8 rounded-xl shadow-xs text-[#17202A]">
        {/* Brand Header */}
        <div className="text-center mb-8">
          <div className="inline-flex p-3 rounded-lg bg-[#102A43] text-white mb-3 shadow-2xs">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <h2 className="text-xl font-bold text-[#17202A] tracking-tight">Create an Account</h2>
          <p className="text-xs text-[#64748B] mt-1.5">Join LegalFlow AI Contract Risk & Redline Studio</p>
        </div>

        {/* Validation Error Alert */}
        {error && (
          <div className="mb-5 p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-[#C62828] font-medium flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-[#C62828]" />
            <span>{error}</span>
          </div>
        )}

        {/* Register Form */}
        <form id="legalflow-register-form" onSubmit={handleSubmit} className="space-y-4" noValidate>
          {/* Full Name Field */}
          <div>
            <label className="block text-xs font-semibold text-[#17202A] mb-1.5">
              Full Name
            </label>
            <div className="relative">
              <User className="w-4 h-4 text-[#64748B] absolute left-3 top-2.5" />
              <input
                type="text"
                value={fullName}
                onChange={(e) => {
                  setFullName(e.target.value);
                  if (error) setError('');
                }}
                placeholder="John Doe"
                className="w-full bg-[#F4F1E8]/40 border border-[#D9D6CC] rounded-lg py-2 pl-9 pr-3 text-xs text-[#17202A] placeholder-[#64748B] focus:outline-none focus:border-[#163A59] focus:ring-1 focus:ring-[#163A59] transition-colors"
              />
            </div>
          </div>

          {/* Email Address Field */}
          <div>
            <label className="block text-xs font-semibold text-[#17202A] mb-1.5">
              Email Address
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-[#64748B] absolute left-3 top-2.5" />
              <input
                type="email"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (error) setError('');
                }}
                placeholder="user@legalflow.ai"
                className="w-full bg-[#F4F1E8]/40 border border-[#D9D6CC] rounded-lg py-2 pl-9 pr-3 text-xs text-[#17202A] placeholder-[#64748B] focus:outline-none focus:border-[#163A59] focus:ring-1 focus:ring-[#163A59] transition-colors"
              />
            </div>
          </div>

          {/* Organization / Law Firm Field */}
          <div>
            <label className="block text-xs font-semibold text-[#17202A] mb-1.5">
              Organization / Company
            </label>
            <div className="relative">
              <Building2 className="w-4 h-4 text-[#64748B] absolute left-3 top-2.5" />
              <input
                type="text"
                value={organization}
                onChange={(e) => {
                  setOrganization(e.target.value);
                  if (error) setError('');
                }}
                placeholder="Acme Legal Corp"
                className="w-full bg-[#F4F1E8]/40 border border-[#D9D6CC] rounded-lg py-2 pl-9 pr-3 text-xs text-[#17202A] placeholder-[#64748B] focus:outline-none focus:border-[#163A59] focus:ring-1 focus:ring-[#163A59] transition-colors"
              />
            </div>
          </div>

          {/* Password Field with Show/Hide toggle */}
          <div>
            <label className="block text-xs font-semibold text-[#17202A] mb-1.5">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-[#64748B] absolute left-3 top-2.5" />
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (error) setError('');
                }}
                placeholder="•••••••• (Min 6 characters)"
                className="w-full bg-[#F4F1E8]/40 border border-[#D9D6CC] rounded-lg py-2 pl-9 pr-9 text-xs text-[#17202A] placeholder-[#64748B] focus:outline-none focus:border-[#163A59] focus:ring-1 focus:ring-[#163A59] transition-colors"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-2.5 text-[#64748B] hover:text-[#17202A] transition-colors cursor-pointer"
                title={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Register Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-2.5 bg-[#163A59] hover:bg-[#102A43] text-white text-xs font-semibold rounded-lg shadow-2xs transition-colors disabled:opacity-50 cursor-pointer"
          >
            {loading ? 'Creating Account & Setting Up Workspace...' : 'Register & Launch Workspace'}
          </button>
        </form>

        {/* Sign In Option */}
        <p className="text-center text-xs text-[#64748B] mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-[#163A59] font-semibold hover:underline">
            Sign In
          </Link>
        </p>
      </div>
    </div>
  );
};
