import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { API_URL } from "../config";
import placeholderImage from "../assets/placeholder-image.jpg";

const BuildCarousel = () => {
  const [builds, setBuilds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const fetchBuilds = async () => {
      try {
        // Fetch top 5 builds
        const buildsResponse = await fetch(`${API_URL}/api/builds/public?limit=5`);
        const buildsData = await buildsResponse.json();
        console.log("Carousel builds:", buildsData);
        setBuilds(buildsData.builds);
      } catch (error) {
        console.error("Error fetching builds:", error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchBuilds();
    
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
  
  return (
    <div className="w-full max-w-4xl mx-auto relative mb-16 overflow-hidden rounded-lg shadow-xl">
      <Link to={`/build/${currentBuild.id}`} className="block">
        <div className="relative h-80 overflow-hidden">
          {/* Featured build info */}
          <div className="absolute inset-0 flex flex-col justify-end p-8 text-white bg-gradient-to-t from-black/70 to-transparent">
            {/* Show placeholder image */}
            <img 
              src={placeholderImage} 
              alt={build.name} 
              className="absolute inset-0 w-full h-full object-cover"
            />
            <div className="flex justify-between items-end relative z-10">
              <div>
                <h2 className="text-3xl font-bold mb-2">{build.name}</h2>
                <p className="text-lg mb-1">
                  {build.cpu ? build.cpu.name : 'No CPU'} | {build.gpu ? build.gpu.name : 'No GPU'}
                </p>
                <p className="text-sm text-slate-300 mb-4">
                  {build.ram ? build.ram.name : 'No RAM'} | {build.storage ? build.storage.name : 'No Storage'}
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
              </div>
            </div>
          </div>
        </div>
      </Link>

      {/* Navigation arrows - outside the Link to avoid conflicts */}
      <button 
        className="absolute left-2 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-black/30 text-white flex justify-center items-center hover:bg-black/50 z-10"
        onClick={(e) => {
          e.stopPropagation();
          prevSlide();
        }}
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6">
          <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
        </svg>
      </button>
      <button 
        className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-black/30 text-white flex justify-center items-center hover:bg-black/50 z-10"
        onClick={(e) => {
          e.stopPropagation();
          nextSlide();
        }}
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6">
          <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
        </svg>
      </button>

      {/* Indicators - outside the Link to avoid conflicts */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex space-x-2 z-10">
        {builds.map((_, index) => (
          <button 
            key={index} 
            className={`w-2 h-2 rounded-full ${index === currentIndex ? 'bg-white' : 'bg-white/50'}`}
            onClick={(e) => {
              e.stopPropagation();
              goToSlide(index);
            }}
          />
        ))}
      </div>
    </div>
  );
};

export default BuildCarousel; 