import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { API_URL } from "../config";

const BuildCarousel = () => {
  const [builds, setBuilds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [componentMaps, setComponentMaps] = useState({});

  useEffect(() => {
    const fetchBuildsAndComponents = async () => {
      try {
        // Fetch top 5 builds
        const buildsResponse = await fetch(`${API_URL}/api/builds/public?limit=5`);
        const buildsData = await buildsResponse.json();
        
        // Fetch component data for displaying details
        const [cpusRes, gpusRes, ramRes, storageRes] = await Promise.all([
          fetch(`${API_URL}/api/cpus`),
          fetch(`${API_URL}/api/gpus`),
          fetch(`${API_URL}/api/ram`),
          fetch(`${API_URL}/api/storage`)
        ]);
        
        const [cpus, gpus, ram, storage] = await Promise.all([
          cpusRes.json(),
          gpusRes.json(),
          ramRes.json(),
          storageRes.json()
        ]);
        
        // Create component maps for lookups
        const cpuMap = Object.fromEntries(cpus.map(cpu => [cpu.id, cpu]));
        const gpuMap = Object.fromEntries(gpus.map(gpu => [gpu.id, gpu]));
        const ramMap = Object.fromEntries(ram.map(ram => [ram.id, ram]));
        const storageMap = Object.fromEntries(storage.map(storage => [storage.id, storage]));
        
        setComponentMaps({ cpuMap, gpuMap, ramMap, storageMap });
        setBuilds(buildsData.builds);
      } catch (error) {
        console.error("Error fetching builds:", error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchBuildsAndComponents();
    
    // Auto rotate carousel every 5 seconds
    const interval = setInterval(() => {
      setCurrentIndex(prevIndex => 
        prevIndex === builds.length - 1 ? 0 : prevIndex + 1
      );
    }, 5000);
    
    return () => clearInterval(interval);
  }, [builds.length]);
  
  const nextSlide = () => {
    setCurrentIndex(prevIndex => 
      prevIndex === builds.length - 1 ? 0 : prevIndex + 1
    );
  };
  
  const prevSlide = () => {
    setCurrentIndex(prevIndex => 
      prevIndex === 0 ? builds.length - 1 : prevIndex - 1
    );
  };
  
  const goToSlide = (index) => {
    setCurrentIndex(index);
  };
  
  if (loading) {
    return (
      <div className="w-full max-w-4xl mx-auto h-80 bg-slate-200 rounded-lg animate-pulse mb-8"></div>
    );
  }
  
  if (builds.length === 0) {
    return null;
  }
  
  const currentBuild = builds[currentIndex];
  const build = currentBuild?.build;
  
  if (!build) return null;
  
  // Get component details
  const cpuInfo = componentMaps.cpuMap?.[build.cpu_id];
  const gpuInfo = componentMaps.gpuMap?.[build.gpu_id];
  const ramInfo = componentMaps.ramMap?.[build.ram_id];
  const storageInfo = componentMaps.storageMap?.[build.storage_id];
  
  return (
    <div className="w-full max-w-4xl mx-auto relative mb-16 overflow-hidden rounded-lg shadow-xl">
      <div className="relative h-80 bg-gradient-to-r from-slate-700 to-slate-900 overflow-hidden">
        {/* Featured build info */}
        <div className="absolute inset-0 flex flex-col justify-end p-8 text-white bg-gradient-to-t from-black/70 to-transparent">
          <div className="flex justify-between items-end">
            <div>
              <h2 className="text-3xl font-bold mb-2">{build.name}</h2>
              <p className="text-lg mb-1">
                {cpuInfo ? cpuInfo.name : 'No CPU'} | {gpuInfo ? gpuInfo.name : 'No GPU'}
              </p>
              <p className="text-sm text-slate-300 mb-4">
                {ramInfo ? ramInfo.name : 'No RAM'} | {storageInfo ? storageInfo.name : 'No Storage'}
              </p>
              
              {/* Show rating if available */}
              {currentBuild.avg_rating > 0 && (
                <div className="flex items-center mb-4">
                  <div className="flex">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <svg 
                        key={star} 
                        fill={star <= Math.round(currentBuild.avg_rating) ? "#FFB800" : "#E5E5E5"} 
                        height="16" 
                        width="16" 
                        className="mr-0.5" 
                        viewBox="0 0 24 24">
                        <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"></path>
                      </svg>
                    ))}
                  </div>
                  <span className="ml-2 text-sm">
                    ({currentBuild.rating_count} reviews)
                  </span>
                </div>
              )}
              
              <Link 
                to={`/build/${currentBuild.id}`} 
                className="inline-block px-4 py-2 bg-blue-600 rounded-lg text-white font-medium hover:bg-blue-700 transition"
              >
                View Build
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation arrows */}
      <button 
        className="absolute left-2 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-black/30 text-white flex justify-center items-center hover:bg-black/50"
        onClick={prevSlide}
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6">
          <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
        </svg>
      </button>
      <button 
        className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-black/30 text-white flex justify-center items-center hover:bg-black/50"
        onClick={nextSlide}
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6">
          <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
        </svg>
      </button>

      {/* Indicators */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex space-x-2">
        {builds.map((_, index) => (
          <button 
            key={index} 
            className={`w-2 h-2 rounded-full ${index === currentIndex ? 'bg-white' : 'bg-white/50'}`}
            onClick={() => goToSlide(index)}
          />
        ))}
      </div>
    </div>
  );
};

const Home = () => {
  return (
    <div className="wrapper bg-gradient-to-b from-slate-300 to-slate-200">
      <div className="flex justify-center items-center min-h-screen pt-16">
        <div className="container px-4 flex flex-col items-center">
          
          <h1 className="text-4xl font-bold text-center text-slate-800 mb-8">Showcase</h1>
          <BuildCarousel />
          
          <p className="text-xl text-slate-700 mt-6 text-center max-w-2xl">
            Skapa din perfekta dator med vår användarvänliga byggverktyg. 
            Jämför komponenter och kontrollera kompatibilitet.
          </p>
          
          <div className="mt-12 flex gap-6 flex-wrap justify-center">
            <Link to="/pcbuilder" className="bg-slate-300 text-black hover:text-gray-700 hover:scale-105 border-2 hover:bg-slate-400 border-slate-600 rounded-lg p-1 shadow-lg">
              Börja Bygga
            </Link>
            <Link to="/savedbuilds" className="bg-slate-300 text-black hover:text-gray-700 hover:scale-105 border-2 hover:bg-slate-400 border-slate-600 rounded-lg p-1 shadow-lg">
              Se Dina Byggen
            </Link>
            <Link to="/createaccount" className="bg-slate-300 text-black hover:text-gray-700 hover:scale-105 border-2 hover:bg-slate-400 border-slate-600 rounded-lg p-1 shadow-lg">
               Skapa Konto
            </Link>
          </div>

          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-4xl">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="font-semibold text-xl mb-2">Kompatibilitetskontroll</h3>
              <p className="text-gray-600">Säkerställ att alla komponenter fungerar perfekt tillsammans.</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="font-semibold text-xl mb-2">Prestandaöversikt</h3>
              <p className="text-gray-600">Få rekommendationer baserade på dina behov.</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="font-semibold text-xl mb-2">Skapa konto</h3>
              <p className="text-gray-600">Skapa konto för att kunna spara dina byggen och få rekommendationer på komponenter.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
