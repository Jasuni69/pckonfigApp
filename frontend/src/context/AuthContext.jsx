import { createContext, useContext, useState, useEffect } from 'react';
import { API_URL } from '../config';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    const storedToken = localStorage.getItem('token');
    if (!storedToken) {
      setLoading(false);
      return;
    }

    try {
      console.log('Checking auth status with token:', storedToken.substring(0, 10) + '...');
      
      const response = await fetch(`${API_URL}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${storedToken}`
        }
      });
      
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        setIsAuthenticated(true);
        setToken(storedToken);
        console.log('Auth check successful - user is authenticated');
      } else {
        console.log('Auth check failed:', response.status);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setIsAuthenticated(false);
        setUser(null);
        setToken(null);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      setIsAuthenticated(false);
      setUser(null);
      setToken(null);
    } finally {
      setLoading(false);
    }
  };

  const refreshToken = async () => {
    if (!token) return;
    
    try {
      console.log('Refreshing token...');
      
      // This is a simple approach that will update the timestamp in the database
      // by calling the /me endpoint which will verify the token is still valid
      const response = await fetch(`${API_URL}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        console.log('Token refresh succeeded');
        // We don't need to update the token since it's the same token
        // but with an updated timestamp in the database
      } else {
        console.error('Token refresh failed, logging out');
        logout();
      }
    } catch (error) {
      console.error('Error refreshing token:', error);
      logout();
    }
  };

  const login = async (newToken, userData) => {
    console.log('Login called with token:', newToken ? newToken.substring(0, 10) + '...' : 'none');
    
    localStorage.setItem('token', newToken);
    if (userData) {
      localStorage.setItem('user', JSON.stringify(userData));
    }
    
    setToken(newToken);
    setIsAuthenticated(true);
    setUser(userData);
    
    console.log('Login successful - user authenticated');
  };

  const logout = () => {
    console.log('Logout called - clearing auth state');
    
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setIsAuthenticated(false);
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{
      isAuthenticated,
      user,
      token,
      loading,
      login,
      logout,
      checkAuthStatus,
      refreshToken
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 