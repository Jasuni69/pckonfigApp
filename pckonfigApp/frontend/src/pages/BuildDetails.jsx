import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { API_URL } from "../config";
import placeholderImage from "../assets/placeholder-image.jpg";

// ... rest of the imports ...

const BuildDetails = () => {
  // ... existing state and functions ...

  return (
    <div className="wrapper bg-gradient-to-b from-slate-400 to-slate-200 pb-28 -mt-24">
      {/* ... other JSX ... */}
      
      {/* Build Image Section */}
      <div className="relative h-96 w-full">
        <img 
          src={placeholderImage} 
          alt={build?.name || "Build Preview"} 
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent flex items-end p-8">
          <div className="text-white">
            <h1 className="text-4xl font-bold mb-2">{build?.name}</h1>
            <p className="text-lg">
              {build?.cpu?.name || 'No CPU'} | {build?.gpu?.name || 'No GPU'}
            </p>
          </div>
        </div>
      </div>

      {/* ... rest of the JSX ... */}
    </div>
  );
};

export default BuildDetails; 