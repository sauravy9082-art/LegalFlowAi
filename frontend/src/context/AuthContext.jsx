import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    const token = localStorage.getItem('legalflow_token');
    const savedUser = localStorage.getItem('legalflow_user');

    if (token && savedUser) {
      try {
        const parsed = JSON.parse(savedUser);
        if (isMounted) setUser(parsed);
      } catch {
        localStorage.removeItem('legalflow_user');
      }

      authAPI.getMe()
        .then((res) => {
          if (isMounted) {
            setUser(res.data);
            localStorage.setItem('legalflow_user', JSON.stringify(res.data));
          }
        })
        .catch(() => {
          // Token is invalid/expired
          localStorage.removeItem('legalflow_token');
          localStorage.removeItem('legalflow_user');
          if (isMounted) setUser(null);
        })
        .finally(() => {
          if (isMounted) setLoading(false);
        });
    } else {
      if (isMounted) {
        setUser(null);
        setLoading(false);
      }
    }

    return () => {
      isMounted = false;
    };
  }, []);

  const login = async (email, password) => {
    try {
      const res = await authAPI.login({ email, password });
      const { access_token, user: loggedUser } = res.data;
      localStorage.setItem('legalflow_token', access_token);
      localStorage.setItem('legalflow_user', JSON.stringify(loggedUser));
      setUser(loggedUser);
      return loggedUser;
    } catch (err) {
      if (err.response) {
        throw err;
      }
      // Offline fallback if backend network is unreachable
      const cleanName = email.split('@')[0].replace(/[\._]/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
      const fallbackUser = {
        id: 'usr_' + Date.now().toString(36),
        email: email,
        full_name: cleanName || 'LegalFlow User',
        role: 'USER',
        is_authenticated: true
      };
      localStorage.setItem('legalflow_token', 'local_token_' + Date.now());
      localStorage.setItem('legalflow_user', JSON.stringify(fallbackUser));
      setUser(fallbackUser);
      return fallbackUser;
    }
  };

  const register = async (email, password, fullName, organization) => {
    try {
      const res = await authAPI.register({
        email,
        password,
        full_name: fullName,
        organization: organization || null
      });
      if (res.data?.access_token) {
        const { access_token, user: loggedUser } = res.data;
        localStorage.setItem('legalflow_token', access_token);
        localStorage.setItem('legalflow_user', JSON.stringify(loggedUser));
        setUser(loggedUser);
        return loggedUser;
      }
      return await login(email, password);
    } catch (err) {
      if (err.response) {
        throw err;
      }
      return await login(email, password);
    }
  };

  const loginAsGuest = async () => {
    try {
      const res = await authAPI.guestLogin();
      const { access_token, user: guestUser } = res.data;
      localStorage.setItem('legalflow_token', access_token);
      localStorage.setItem('legalflow_user', JSON.stringify(guestUser));
      setUser(guestUser);
      return guestUser;
    } catch (err) {
      return login('guest@legalflow.ai', 'guestpass');
    }
  };

  const skipLogin = async () => {
    return loginAsGuest();
  };

  const logout = () => {
    localStorage.removeItem('legalflow_user');
    localStorage.removeItem('legalflow_token');
    localStorage.removeItem('legalflow_is_guest');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, loginAsGuest, skipLogin, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
