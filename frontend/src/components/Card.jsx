import { useState, useEffect } from "react";
import { X } from "lucide-react";

const Card = ({ title, img, className = "", onSelect, options, filterRequirements }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [selected, setSelected] = useState(null);
  const [choices, setChoices] = useState([]);
  const [search, setSearch] = useState("");
  const [components, setComponents] = useState([]);

  const purposeOptions = [
    { name: "1080p Gaming", price: "0" },
    { name: "1440p Gaming", price: "0" },
    { name: "4K Gaming", price: "0" },
    { name: "Programmera/Utveckla", price: "0" },
    { name: "AI/Machine Learning", price: "0" },
    { name: "3D Rendering", price: "0" },
    { name: "Video Redigering", price: "0" },
    { name: "Basic Användning", price: "0" },
  ];

  useEffect(() => {
    if (options === "purpose") {
      setChoices(purposeOptions);
    } else {
      const fetchComponents = async () => {
        try {
          console.log('Fetching components for:', options);
          console.log('Filter requirements:', filterRequirements);
          
          const response = await fetch(`/api/${options}`);
          if (!response.ok) {
            console.error(`Error fetching ${options}: ${response.status}`);
            setComponents([]);
            setChoices([]);
            return;
          }
          
          const data = await response.json();
          
          let filteredData = data;
          
          if (filterRequirements && Object.keys(filterRequirements).length > 0) {
            console.log(`Filtering ${options} with requirements:`, filterRequirements);
            
            filteredData = data.filter(component => {
              if (!component) return false;
              
              // CPU/Motherboard socket compatibility
              if (filterRequirements.socket && (options === 'cpus' || options === 'motherboards')) {
                const reqSocket = filterRequirements.socket.toLowerCase().replace(/socket\s*/i, '');
                const compSocket = (component.socket || '').toLowerCase().replace(/socket\s*/i, '');
                
                // Special handling for Intel sockets
                if (reqSocket.includes('1700')) {
                  const matches = compSocket.includes('1700');
                  console.log(`${options} ${component.name} socket check:`, {
                    required: reqSocket,
                    actual: compSocket,
                    matches
                  });
                  return matches;
                }
                
                const matches = compSocket.includes(reqSocket);
                console.log(`${options} ${component.name} socket check:`, {
                  required: reqSocket,
                  actual: compSocket,
                  matches
                });
                return matches;
              }

              // PSU minimum wattage requirement for GPU
              if (filterRequirements.minWattage && options === 'psus') {
                const matches = component.wattage >= filterRequirements.minWattage;
                console.log(`PSU ${component.name} wattage check:`, {
                  required: filterRequirements.minWattage,
                  actual: component.wattage,
                  matches
                });
                return matches;
              }

              // GPU maximum wattage requirement for PSU
              if (filterRequirements.maxWattage && options === 'gpus') {
                const gpuWattage = component.recommended_wattage || 0;
                const matches = gpuWattage <= filterRequirements.maxWattage;
                console.log(`GPU ${component.name} wattage check:`, {
                  maxAllowed: filterRequirements.maxWattage,
                  required: gpuWattage,
                  matches
                });
                return matches;
              }

              // Case form factor compatibility
              if (filterRequirements.formFactor && options === 'case') {
                const reqFormFactor = filterRequirements.formFactor.toLowerCase();
                const compFormFactor = component.form_factor.toLowerCase();
                const matches = compFormFactor.includes(reqFormFactor);
                console.log(`Case ${component.name} form factor check:`, {
                  required: reqFormFactor,
                  actual: compFormFactor,
                  matches
                });
                return matches;
              }

              return true;
            });
            
            console.log(`Filtered ${options} results:`, filteredData);
          }
          
          setComponents(filteredData);
          setChoices(filteredData);
        } catch (error) {
          console.error(`Error fetching ${options}:`, error);
          setComponents([]);
          setChoices([]);
        }
      };

      fetchComponents();
    }
  }, [options, filterRequirements]);

  const filteredChoices = search
    ? (options === "purpose" ? choices : choices).filter((opt) =>
        opt.name.toLowerCase().includes(search.toLowerCase())
      )
    : choices;

  const handleSelect = (option) => {
    setSelected(option);
    onSelect(option);
    setIsOpen(false);
    setSearch("");
  };

  return (
    <div className={`relative bg-slate-200 rounded-lg p-4 ${className}`}>
      <div className="flex items-center gap-2 mb-2">
        {img && <img src={img} alt={title} className="w-8 h-8" />}
        <h3 className="text-lg font-semibold">{title}</h3>
      </div>
      
      <div
        className="bg-slate-300 shadow-md p-6 cursor-pointer hover:bg-slate-400 transition-colors"
        onClick={() => setIsOpen(true)}
      >
        {selected ? (
          <div className="flex justify-between items-center">
            <span>{selected.name}</span>
            {selected.price !== "0" ? `${selected.price}kr` : ""}
          </div>
        ) : (
          `Välj ${title}`
        )}
      </div>

      {isOpen && (
        <div className="fixed inset-0 flex items-center justify-center z-50">
          <div
            className="bg-slate-400 p-8 rounded-lg border-2 border-slate-800 shadow-lg w-96 max-w-[90vw]"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-black">{title}</h2>
              <button
                className="bg-slate-300 rounded-lg p-2 border-2 border-slate-800 shadow-lg hover:bg-slate-400 transition-colors"
                onClick={() => setIsOpen(false)}
              >
                <X className="h-5 w-5 text-black hover:scale-105" />
              </button>
            </div>

            {/* Search Bar */}
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full p-2 rounded border border-gray-500 mb-4"
              placeholder="Sök..."
            />

            {/* Filtered Dropdown List */}
            <div className="bg-white border border-gray-300 rounded shadow-lg max-h-[60vh] overflow-y-auto">
              {filteredChoices.length > 0 ? (
                <ul>
                  {filteredChoices.map((option, index) => (
                    <li
                      key={index}
                      onClick={() => handleSelect(option)}
                      className="p-4 cursor-pointer hover:bg-gray-200 border-b border-gray-100 flex justify-between items-center"
                    >
                      <span>{option.name}</span>
                      {option.price !== "0" && <span>{option.price}kr</span>}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="p-4 text-gray-600">Inga resultat hittades.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Card;
