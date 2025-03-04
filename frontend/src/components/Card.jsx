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
          const response = await fetch(`/api/${options}`);
          const data = await response.json();
          console.log(`Fetched ${options} data:`, data);
          
          let filteredData = data;
          
          if (filterRequirements && Object.keys(filterRequirements).length > 0) {
            console.log(`Filtering ${options} with requirements:`, filterRequirements);
            
            filteredData = data.filter(component => {
              // Socket compatibility
              if (filterRequirements.socket && component.socket) {
                // Clean up socket strings for comparison
                const reqSocket = filterRequirements.socket.toLowerCase().replace('socket ', '');
                const compSocket = component.socket.toLowerCase().replace('socket ', '');
                const matches = compSocket.includes(reqSocket);
                console.log(`Socket check for ${component.name}: ${matches} (${compSocket} vs ${reqSocket})`);
                return matches;
              }
              
              // PSU wattage requirement
              if (filterRequirements.minWattage && component.wattage) {
                const matches = component.wattage >= filterRequirements.minWattage;
                console.log(`Wattage check for ${component.name}: ${matches} (${component.wattage} vs ${filterRequirements.minWattage})`);
                return matches;
              }
              
              // Form factor compatibility
              if (filterRequirements.formFactor && component.form_factor) {
                // Handle multiple form factors and variations
                const reqFormFactor = filterRequirements.formFactor.toLowerCase();
                const compFormFactors = component.form_factor.toLowerCase().split(',').map(f => f.trim());
                const matches = compFormFactors.some(f => 
                  f.includes(reqFormFactor) || 
                  (f.includes('utökad') && reqFormFactor === 'atx') ||
                  (reqFormFactor.includes('utökad') && f === 'atx')
                );
                console.log(`Form factor check for ${component.name}: ${matches} (${compFormFactors} vs ${reqFormFactor})`);
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
