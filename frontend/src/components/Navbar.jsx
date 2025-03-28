import React from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import pcLogo from "../assets/logos/pc.svg";

const Navbar = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const location = useLocation();

  return (
    <nav className="h-auto min-w-full max-w-full fixed top-0 bg-white z-50">
      {/* Top Bar with subtle gradient */}
      <div className="flex h-16 items-center px-6 bg-gradient-to-r from-slate-50 to-white border-b border-slate-200">
        {/* Logo Section */}
        <div className="flex flex-1">
          <Link 
            to="/" 
            className="flex items-center gap-3 hover:opacity-80 transition-all duration-200 group"
          >
            <img 
              src={pcLogo} 
              alt="PCkonfig Logo" 
              className="h-9 w-9 group-hover:scale-105 transition-transform duration-200"
            />
            <span className="text-xl font-bold bg-gradient-to-r from-slate-800 to-slate-600 bg-clip-text text-transparent">
              PCkonfig.se
            </span>
          </Link>
        </div>

        {/* Auth Section */}
        <div className="flex items-center gap-6">
          {isAuthenticated ? (
            <div className="flex items-center gap-4">
              <span className="text-slate-600 hidden sm:inline font-medium">
                Välkommen, {user?.email}
              </span>
              <button 
                onClick={logout}
                className="px-4 py-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-all duration-200 font-medium"
              >
                Logga ut
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <Link 
                to="/login" 
                className="px-4 py-2 text-slate-600 hover:text-slate-100 hover:bg-slate-700 rounded-lg transition-all duration-200 font-medium"
              >
                Logga in
              </Link>
              <Link 
                to="/createaccount" 
                className="px-4 py-2 bg-slate-800 text-white rounded-lg hover:bg-slate-700 hover:scale-105 transition-all duration-200 shadow-sm hover:shadow-md font-medium"
              >
                Skapa konto
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Navigation Bar */}
      <div className="bg-gradient-to-r from-slate-700 to-slate-800 h-12 flex items-center px-6 shadow-md">
        <div className="flex gap-3 items-center">
          <NavLink to="/pcbuilder" currentPath={location.pathname}>
            Bygg din PC
          </NavLink>
          <NavLink to="/pcparts" currentPath={location.pathname}>
            PC-delar
          </NavLink>
          {isAuthenticated && (
            <NavLink to="/savedbuilds" currentPath={location.pathname}>
              Sparade byggen
            </NavLink>
          )}
          <NavLink to="/buildgallery" currentPath={location.pathname}>
            Galleri
          </NavLink>
        </div>
      </div>
    </nav>
  );
};

// Custom NavLink component with modern styling
const NavLink = ({ to, children, currentPath }) => (
  <Link 
    to={to} 
    className={`
      px-4 py-1.5 
      rounded-lg
      font-medium
      transition-all duration-200
      ${currentPath === to 
        ? 'bg-white text-slate-800 shadow-md' 
        : 'bg-slate-600/50 text-white hover:bg-slate-500/50 shadow-sm hover:shadow-md'}
    `}
  >
    {children}
  </Link>
);

export default Navbar;
