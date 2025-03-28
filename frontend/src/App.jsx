import React from "react";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Home from "./pages/Home";
import About from "./pages/About";
import Contact from "./pages/Contact";
import PcBuilder from "./pages/PcBuilder";
import CreateAccount from "./pages/CreateAccount";
import Login from "./pages/Login";
import { AuthProvider } from "./context/AuthContext";
import SavedBuilds from "./pages/SavedBuilds";
import BuildGallery from "./pages/BuildGallery";
const App = () => {
  return (
    <AuthProvider>
      <Router>
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/pcbuilder" element={<PcBuilder />} />
          <Route path="/createaccount" element={<CreateAccount />} />
          <Route path="/login" element={<Login />} />
          <Route path="/savedbuilds" element={<SavedBuilds />} />
          <Route path="/buildgallery" element={<BuildGallery />} />
        </Routes>
        <Footer />
      </Router>
    </AuthProvider>
  );
};

export default App;
