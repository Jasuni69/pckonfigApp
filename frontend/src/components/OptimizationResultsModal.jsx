import React from 'react';

const OptimizationResultsModal = ({ isOpen, onClose, optimizationResult }) => {
  if (!isOpen || !optimizationResult) return null;

  const {
    cpu, gpu, motherboard, ram, psu, case: pcCase, storage, cooler, explanation
  } = optimizationResult;

  // Helper function to create component cards
  const ComponentCard = ({ title, component, details = [] }) => {
    if (!component) return null;
    
    return (
      <div className="bg-slate-100 rounded-lg p-3 shadow">
        <h3 className="font-bold text-slate-800">{title}</h3>
        <p className="text-base mb-1">{component.name}</p>
        {details.map((detail, index) => (
          <p key={index} className="text-sm text-slate-600">
            {detail.label}: {component[detail.property] || 'N/A'}
          </p>
        ))}
      </div>
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-100 bg-opacity-30">
      <div className="bg-white rounded-lg w-11/12 max-w-4xl max-h-[90vh] overflow-y-auto shadow-xl">
        <div className="p-4 border-b border-slate-200 flex justify-between items-center">
          <h2 className="text-xl font-bold text-slate-800">Optimeringsresultat</h2>
          <button 
            onClick={onClose}
            className="text-slate-500 hover:text-slate-700"
          >
            ✕
          </button>
        </div>
        
        <div className="p-6">
          {/* Explanation Section */}
          <div className="mb-6 p-4 bg-slate-100 rounded-lg">
            <h3 className="font-bold mb-2 text-slate-800">AI Rekommendation</h3>
            <p className="text-slate-700">{explanation}</p>
          </div>
          
          {/* Components Grid */}
          <h3 className="font-bold mb-3 text-slate-800">Rekommenderade komponenter</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <ComponentCard 
              title="Processor" 
              component={cpu} 
              details={[
                { label: "Socket", property: "socket" },
                { label: "Cores", property: "cores" }
              ]} 
            />
            <ComponentCard 
              title="Grafikkort" 
              component={gpu} 
              details={[
                { label: "Memory", property: "memory" }
              ]} 
            />
            <ComponentCard 
              title="Moderkort" 
              component={motherboard} 
              details={[
                { label: "Socket", property: "socket" },
                { label: "Form Factor", property: "form_factor" }
              ]} 
            />
            <ComponentCard 
              title="RAM-minne" 
              component={ram} 
              details={[
                { label: "Capacity", property: "capacity" },
                { label: "Speed", property: "speed" }
              ]} 
            />
            <ComponentCard 
              title="Nätaggregat" 
              component={psu} 
              details={[
                { label: "Wattage", property: "wattage" }
              ]} 
            />
            <ComponentCard 
              title="Chassi" 
              component={pcCase} 
              details={[
                { label: "Form Factor", property: "form_factor" }
              ]} 
            />
            <ComponentCard 
              title="Lagring" 
              component={storage} 
              details={[
                { label: "Capacity", property: "capacity" },
                { label: "Type", property: "type" }
              ]} 
            />
            <ComponentCard 
              title="CPU-kylare" 
              component={cooler} 
              details={[
                { label: "Type", property: "type" }
              ]} 
            />
          </div>
          
          {/* Action Buttons */}
          <div className="flex justify-end mt-4 space-x-3">
            <button
              onClick={onClose}
              className="bg-slate-300 text-black hover:text-gray-700 hover:scale-105 border-2 hover:bg-slate-400 border-slate-600 rounded-lg px-4 py-2 shadow-lg"
            >
              Stäng
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OptimizationResultsModal; 