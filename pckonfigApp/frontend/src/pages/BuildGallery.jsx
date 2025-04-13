import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { API_URL } from "../config";
import placeholderImage from "../assets/placeholder-image.jpg";

// ... rest of the imports ...

const BuildGallery = () => {
  // ... existing state and functions ...

  return (
    <div className="wrapper bg-gradient-to-b from-slate-400 to-slate-200 pb-28 -mt-24">
      {/* ... other JSX ... */}
      
      {/* Build Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {builds.map((build) => (
          <Link 
            key={build.id} 
            to={`/build/${build.id}`}
            className="group"
          >
            <div className="bg-white rounded-lg shadow-lg overflow-hidden transition-transform duration-300 group-hover:scale-105">
              <div className="relative h-48">
                <img 
                  src={placeholderImage} 
                  alt={build.name} 
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent flex items-end p-4">
                  <div className="text-white">
                    <h3 className="text-xl font-bold">{build.name}</h3>
                    <p className="text-sm">
                      {build.cpu?.name || 'No CPU'} | {build.gpu?.name || 'No GPU'}
                    </p>
                  </div>
                </div>
              </div>
              {/* ... rest of the build card content ... */}
            </div>
          </Link>
        ))}
      </div>

      {/* ... rest of the JSX ... */}
    </div>
  );
};

export default BuildGallery; 