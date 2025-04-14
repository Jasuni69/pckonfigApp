import React from 'react';
import Navbar from './Navbar';
import Footer from './Footer';

const Layout = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow bg-gradient-to-b from-slate-300 to-slate-200 pt-20">
        {children}
      </main>
      <Footer />
    </div>
  );
};

export default Layout; 