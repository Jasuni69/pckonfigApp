import React, { Suspense, lazy } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import ErrorBoundary from "./components/ErrorBoundary";
import Footer from "./components/Footer";
import Home from "./pages/Home";
import About from "./pages/About";
import Contact from "./pages/Contact";
import CreateAccount from "./pages/CreateAccount";
import BuildGallery from "./pages/BuildGallery";
import BuildDetail from "./pages/BuildDetail";

// Lazy load pages for better performance
const PcBuilder = lazy(() => import("./pages/PcBuilder"));
const SavedBuilds = lazy(() => import("./pages/SavedBuilds"));
const Login = lazy(() => import("./pages/Login"));
const Register = lazy(() => import("./pages/Register"));

// Loading component
const LoadingSpinner = () => (
  <div className="min-h-screen flex items-center justify-center">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
  </div>
);

const App = () => {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <div className="min-h-screen bg-gray-50">
            <Navbar />
            <Suspense fallback={<LoadingSpinner />}>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/about" element={<About />} />
                <Route path="/contact" element={<Contact />} />
                <Route path="/pcbuilder" element={<PcBuilder />} />
                <Route path="/createaccount" element={<CreateAccount />} />
                <Route path="/login" element={<Login />} />
                <Route path="/savedbuilds" element={<SavedBuilds />} />
                <Route path="/build/:id" element={<BuildDetail />} />
                <Route path="/buildgallery" element={<BuildGallery />} />
              </Routes>
            </Suspense>
            <Footer />
          </div>
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
};

export default App;
