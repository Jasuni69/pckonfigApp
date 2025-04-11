import React, { useEffect } from 'react';

const OptimizationResultsModal = ({ isOpen, onClose, optimizationResult }) => {
  if (!isOpen || !optimizationResult) return null;

  // Add debug logging to check what data we're receiving
  useEffect(() => {
    console.log("Optimization result received:", optimizationResult);
    
    // Log specifically to check if recommended_components exists
    console.log("recommended_components exists:", 'recommended_components' in optimizationResult);
    console.log("recommended_components value:", optimizationResult.recommended_components);
    
    // Check if it's empty or has content
    if (optimizationResult.recommended_components) {
      console.log("recommended_components keys:", Object.keys(optimizationResult.recommended_components));
      
      // Check counts for each component type
      const counts = {};
      Object.entries(optimizationResult.recommended_components).forEach(([key, value]) => {
        counts[key] = Array.isArray(value) ? value.length : 0;
      });
      console.log("Component counts:", counts);
    }
  }, [optimizationResult]);

  const {
    explanation, component_analysis, recommended_components = {}
  } = optimizationResult;
  
  // Get the first recommended component of each type
  const getFirstRecommendation = (type) => {
    const components = recommended_components?.[type] || [];
    return components.length > 0 ? components[0] : null;
  };
  
  // Get CPU, GPU, etc. from recommended_components
  const cpu = getFirstRecommendation('cpus');
  const gpu = getFirstRecommendation('gpus');
  const motherboard = getFirstRecommendation('motherboards');
  const ram = getFirstRecommendation('ram');
  const psu = getFirstRecommendation('psus');
  const pcCase = getFirstRecommendation('cases');
  const storage = getFirstRecommendation('storage');
  const cooler = getFirstRecommendation('coolers');

  // Helper function to create component cards
  const ComponentCard = ({ title, component, details = [] }) => {
    if (!component) return null;
    
    return (
      <div className="bg-slate-100 rounded-lg p-3 shadow">
        <h3 className="font-bold text-slate-800">{title}</h3>
        <p className="text-base mb-1">{component.name}</p>
        {details.map((detail, index) => (
          component[detail.property] ? (
            <p key={index} className="text-sm text-slate-600">
              {detail.label}: {component[detail.property]}
            </p>
          ) : null
        ))}
        <p className="text-sm font-semibold text-blue-600 mt-2">{component.price ? `${component.price} kr` : ''}</p>
      </div>
    );
  };

  // Component Analysis section
  const ComponentAnalysis = () => {
    if (!component_analysis) return null;
    
    const { compatibility_issues, suggested_upgrades, missing_components, analysis } = component_analysis;
    
    // If there's nothing to show, don't render the section
    if (
      (!compatibility_issues || compatibility_issues.length === 0) && 
      (!suggested_upgrades || suggested_upgrades.length === 0) &&
      (!missing_components || missing_components.length === 0) &&
      (!analysis || analysis.length === 0)
    ) {
      return null;
    }
    
    // Helper function to translate component type to Swedish
    const translateComponentType = (type) => {
      const translations = {
        'cpu': 'Processor',
        'gpu': 'Grafikkort',
        'motherboard': 'Moderkort',
        'ram': 'RAM-minne',
        'psu': 'Nätaggregat',
        'case': 'Chassi',
        'storage': 'Lagring',
        'cooler': 'CPU-kylare'
      };
      return translations[type] || type;
    };
    
    return (
      <div className="mt-6 mb-6">
        <h3 className="font-bold mb-3 text-slate-800">Komponentanalys</h3>
        
        {/* General Analysis */}
        {analysis && analysis.length > 0 && (
          <div className="mb-4 p-3 bg-slate-100 rounded-lg">
            {analysis.map((item, index) => (
              <p key={index} className="mb-2">{item.message}</p>
            ))}
          </div>
        )}
        
        {/* Missing Components */}
        {missing_components && missing_components.length > 0 && (
          <div className="mb-4">
            <h4 className="font-semibold mb-2 text-slate-700">Saknade komponenter</h4>
            <ul className="list-disc pl-5 space-y-1">
              {missing_components.map((item, index) => (
                <li key={index} className="text-amber-700">
                  <span className="font-medium">{translateComponentType(item.component_type)}:</span> {item.message}
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {/* Compatibility Issues */}
        {compatibility_issues && compatibility_issues.length > 0 && (
          <div className="mb-4">
            <h4 className="font-semibold mb-2 text-slate-700">Kompatibilitetsproblem</h4>
            <ul className="list-disc pl-5 space-y-1">
              {compatibility_issues.map((item, index) => (
                <li key={index} className="text-red-600">
                  <span className="font-medium">
                    {item.component_types.map(type => translateComponentType(type)).join(' & ')}:
                  </span> {item.message}
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {/* Suggested Upgrades */}
        {suggested_upgrades && suggested_upgrades.length > 0 && (
          <div className="mb-4">
            <h4 className="font-semibold mb-2 text-slate-700">Föreslagna uppgraderingar</h4>
            <ul className="list-disc pl-5 space-y-1">
              {suggested_upgrades.map((item, index) => (
                <li key={index} className="text-blue-600">
                  <span className="font-medium">{translateComponentType(item.component_type)}:</span> {item.message}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  // Check if we have any recommended components to display
  const hasRecommendations = Object.values(recommended_components || {}).some(
    list => Array.isArray(list) && list.length > 0
  );

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
            <p className="text-slate-700 whitespace-pre-line">{explanation}</p>
          </div>
          
          {/* Component Analysis */}
          <ComponentAnalysis />
          
          {/* Components Grid */}
          {hasRecommendations && (
            <>
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
                    { label: "Capacity", property: "capacity" }
                  ]} 
                />
                <ComponentCard 
                  title="CPU-kylare" 
                  component={cooler} 
                  details={[]} 
                />
              </div>
            </>
          )}
          {!hasRecommendations && (
            <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg mb-6">
              <p className="text-amber-800">
                Inga specifika komponentrekommendationer tillgängliga för tillfället. 
                Vänligen se komponentanalys ovan för förslag på uppgraderingar.
              </p>
            </div>
          )}
          
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