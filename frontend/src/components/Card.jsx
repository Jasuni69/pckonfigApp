import { useState, useEffect } from "react";
import { X } from "lucide-react";
import { FiInfo } from 'react-icons/fi';
import { API_URL } from '../config';

const normalizeFormFactor = (formFactor) => {
  if (!formFactor) return '';
  
  // Convert to string in case it's not
  const ff = String(formFactor).toLowerCase().trim();
  
  // Handle common variations and Swedish translations
  if (ff.includes('utökad') || ff.includes('extended') || ff.includes('e-atx')) return 'e-atx';
  if (ff.includes('ssi eeb') || ff.includes('eeb')) return 'ssi-eeb';
  if (ff.includes('micro')) return 'micro-atx';
  if (ff.includes('mini-mini')) return 'mini-itx'; 
  if (ff.includes('mini')) return 'mini-itx';
  if (ff === 'itx') return 'mini-itx'; // Explicitly handle ITX as mini-itx
  if (ff.includes('itx')) return 'mini-itx'; // Handle any variant containing ITX
  if (ff === 'atx' || (ff.includes('atx') && !ff.includes('micro') && !ff.includes('mini'))) return 'atx';
  
  // Log unexpected form factors
  console.log('Unexpected form factor:', formFactor);
  return ff; // Return lowercase trimmed version 
};

// Updated compatibility map with lowercase keys and SSI EEB support
const formFactorCompatibility = {
  "ssi-eeb": ["ssi-eeb", "e-atx", "atx", "micro-atx", "mini-itx"],
  "e-atx": ["e-atx", "atx", "micro-atx", "mini-itx"],
  "atx": ["atx", "micro-atx", "mini-itx"],
  "micro-atx": ["micro-atx", "mini-itx"],
  "mini-itx": ["mini-itx"]
};

const GuideContent = ({ type }) => {
  switch(type) {
    case 'cases':
      return (
        <div className="p-4">
          <h4 className="font-bold mb-2">Datorlådor - Guide</h4>
          <ul className="space-y-2">
            <li><span className="font-semibold">E-ATX:</span> Största storleken (305 × 330mm+)</li>
            <li><span className="font-semibold">ATX:</span> Standard storlek (305 × 244mm)</li>
            <li><span className="font-semibold">Micro-ATX:</span> Mellanstor (244 × 244mm)</li>
            <li><span className="font-semibold">Mini-ITX:</span> Kompakt (170 × 170mm)</li>
            <li className="mt-2"><span className="font-semibold">Tips:</span> Kontrollera även:</li>
            <ul className="ml-4">
              <li>- Plats för grafikkort</li>
              <li>- Kylningslösningar</li>
              <li>- Kabeldragning</li>
            </ul>
          </ul>
        </div>
      );
    
    case 'motherboards':
      return (
        <div className="p-4">
          <h4 className="font-bold mb-2">Moderkort - Guide</h4>
          <ul className="space-y-2">
            <li><span className="font-semibold">Form Faktorer:</span></li>
            <ul className="ml-4 mb-2">
              <li>- E-ATX: 305 × 330mm</li>
              <li>- ATX: 305 × 244mm</li>
              <li>- Micro-ATX: 244 × 244mm</li>
              <li>- Mini-ITX: 170 × 170mm</li>
            </ul>
            <li><span className="font-semibold">Viktiga Funktioner:</span></li>
            <ul className="ml-4">
              <li>- CPU Socket (AM4/AM5/LGA1700)</li>
              <li>- RAM-typ (DDR4/DDR5)</li>
              <li>- M.2 platser</li>
            </ul>
          </ul>
        </div>
      );
    
    case 'cpus':
      return (
        <div className="p-4">
          <h4 className="font-bold mb-2">Processorer - Guide</h4>
          <ul className="space-y-2">
            <li><span className="font-semibold">AMD Socklar:</span></li>
            <ul className="ml-4 mb-2">
              <li>- AM5: Nyaste, DDR5</li>
              <li>- AM4: Tidigare gen, DDR4</li>
            </ul>
            <li><span className="font-semibold">Intel Socklar:</span></li>
            <ul className="ml-4">
              <li>- LGA 1851: Intel Ultra (Arrow Lake)</li>
              <li>- LGA 1700: 12:e/13:e/14:e gen</li>
              <li>- LGA 1200: 10:e/11:e gen</li>
            </ul>
            <li className="mt-2 text-red-600 font-semibold">OBS: Intel Ultra (Socket 1851) kräver särskilda moderkort designade för denna socket.</li>
          </ul>
        </div>
      );

    case 'ram':
      return (
        <div className="p-4">
          <h4 className="font-bold mb-2">RAM-Minne - Guide</h4>
          <ul className="space-y-2">
            <li><span className="font-semibold">Typer:</span></li>
            <ul className="ml-4 mb-2">
              <li>- DDR5: Nyaste standarden</li>
              <li>- DDR4: Fortfarande vanlig</li>
            </ul>
            <li><span className="font-semibold">Viktigt att Tänka På:</span></li>
            <ul className="ml-4">
              <li>- Hastighet (MHz)</li>
              <li>- Kapacitet (GB)</li>
              <li>- Latency (CL)</li>
            </ul>
          </ul>
        </div>
      );

    case 'gpus':
      return (
        <div className="p-4">
          <h4 className="font-bold mb-2">Grafikkort - Guide</h4>
          <ul className="space-y-2">
            <li><span className="font-semibold">Tillverkare:</span></li>
            <ul className="ml-4 mb-2">
              <li>- NVIDIA: GeForce RTX/GTX</li>
              <li>- AMD: Radeon RX</li>
            </ul>
            <li><span className="font-semibold">Viktiga Specifikationer:</span></li>
            <ul className="ml-4">
              <li>- VRAM (GB)</li>
              <li>- Strömförbrukning (W)</li>
              <li>- Fysisk storlek</li>
            </ul>
          </ul>
        </div>
      );

    case 'storage':
      return (
        <div className="p-4">
          <h4 className="font-bold mb-2">Lagring - Guide</h4>
          <ul className="space-y-2">
            <li><span className="font-semibold">SSD Typer:</span></li>
            <ul className="ml-4 mb-2">
              <li>- NVMe M.2: Snabbast</li>
              <li>- SATA M.2: Mellannivå</li>
              <li>- SATA 2.5": Standard</li>
            </ul>
            <li><span className="font-semibold">HDD:</span></li>
            <ul className="ml-4">
              <li>- 3.5": Standard storlek</li>
              <li>- 7200/5400 RPM</li>
            </ul>
          </ul>
        </div>
      );

    case 'coolers':
      return (
        <div className="p-4">
          <h4 className="font-bold mb-2">CPU-Kylare - Guide</h4>
          <ul className="space-y-2">
            <li><span className="font-semibold">Typer:</span></li>
            <ul className="ml-4 mb-2">
              <li>- Luftkylning: Traditionell</li>
              <li>- AIO Vattenkylning: Modern</li>
            </ul>
            <li><span className="font-semibold">Att Tänka På:</span></li>
            <ul className="ml-4">
              <li>- TDP-kapacitet</li>
              <li>- Socket-kompatibilitet</li>
              <li>- Fysisk storlek</li>
            </ul>
          </ul>
        </div>
      );

    case 'psus':
      return (
        <div className="p-4">
          <h4 className="font-bold mb-2">Nätaggregat - Guide</h4>
          <ul className="space-y-2">
            <li><span className="font-semibold">Effektivitet:</span></li>
            <ul className="ml-4 mb-2">
              <li>- 80+ Titanium: Bäst</li>
              <li>- 80+ Platinum/Gold: Mycket bra</li>
              <li>- 80+ Bronze: Standard</li>
            </ul>
            <li><span className="font-semibold">Viktigt:</span></li>
            <ul className="ml-4">
              <li>- Watt-tal</li>
              <li>- Modularitet</li>
              <li>- Kabeltyper</li>
            </ul>
          </ul>
        </div>
      );

    default:
      return null;
  }
};

const Card = ({ title, img, className = "", onSelect, options, filterRequirements }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [showGuide, setShowGuide] = useState(false);
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
    if (options === "purpose" || options === "usage") {
      setChoices(purposeOptions);
    } else {
      const fetchComponents = async () => {
        try {
          console.log('🔍 DEBUGGING CARD COMPONENT:');
          console.log('  - Component type:', options);
          console.log('  - API_URL from config:', API_URL);
          console.log('  - Full API endpoint:', `${API_URL}/api/${options}`);
          console.log('  - Filter requirements:', filterRequirements);
          
          // Test if API_URL is accessible
          console.log('📡 Testing API connection...');
          
          const response = await fetch(`${API_URL}/api/${options}`);
          
          console.log('📊 API Response Details:');
          console.log('  - Status:', response.status);
          console.log('  - Status Text:', response.statusText);
          console.log('  - Headers:', Object.fromEntries(response.headers.entries()));
          console.log('  - URL:', response.url);
          console.log('  - OK:', response.ok);
          
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}, statusText: ${response.statusText}`);
          }
          
          const data = await response.json();
          
          console.log('📦 Data received:');
          console.log('  - Type:', typeof data);
          console.log('  - Is Array:', Array.isArray(data));
          console.log('  - Length:', data?.length || 'N/A');
          console.log('  - First item:', data?.[0] || 'No items');
          console.log('  - Sample data structure:', data?.slice(0, 2) || 'No data');
          
          if (!Array.isArray(data)) {
            console.error('❌ Data is not an array:', data);
            throw new Error('API response is not an array');
          }
          
          if (data.length === 0) {
            console.warn('⚠️ No data received from API');
            setComponents([]);
            setChoices([]);
            return;
          }
          
          // Log all components with their form factors before filtering
          if (options === 'motherboards' || options === 'cases') {
            console.log(`🔧 All ${options} before filtering:`, data.map(item => ({
              name: item.name, 
              form_factor: item.form_factor,
              normalized: normalizeFormFactor(item.form_factor)
            })));
          }
          
          let filteredData = data;
          
          if (filterRequirements && Object.keys(filterRequirements).length > 0) {
            console.log(`🔍 Filtering ${options} with requirements:`, filterRequirements);
            
            filteredData = data.filter(component => {
              // CPU/Motherboard socket compatibility
              if (filterRequirements.socket && (options === 'cpus' || options === 'motherboards')) {
                const reqSocket = filterRequirements.socket.toLowerCase().replace('socket ', '');
                const compSocket = (component.socket || '').toLowerCase().replace('socket ', '');
                
                // Special case for Intel Ultra Socket 1851 - only compatible with 1851 motherboards
                if (reqSocket.includes('1851') || compSocket.includes('1851')) {
                  // Exact match required for Arrow Lake processors and motherboards
                  return reqSocket.includes('1851') && compSocket.includes('1851');
                }
                
                // Special case for AM4/AM5 vs Socket AM4/AM5
                if ((reqSocket === 'am4' && compSocket === 'am4') ||
                    (reqSocket === 'am5' && compSocket === 'am5')) {
                  return true;
                }
                
                // For other sockets, partial matching is okay (e.g., 1700 matches 1700 Raptor Lake)
                const matches = compSocket.includes(reqSocket) || reqSocket.includes(compSocket);
                console.log(`Socket compatibility check: required='${reqSocket}', component='${compSocket}', matches=${matches}`);
                return matches;
              }
              
              // Motherboard form factor compatibility with case 
              if (filterRequirements.formFactor && options === 'motherboards') {
                const caseFormFactor = normalizeFormFactor(filterRequirements.formFactor);
                const moboFormFactor = normalizeFormFactor(component.form_factor);
                
                // A case can fit these motherboard form factors
                const compatibleFormFactors = formFactorCompatibility[caseFormFactor] || [caseFormFactor];
                
                const isCompatible = compatibleFormFactors.includes(moboFormFactor);
                
                console.log(`Checking if motherboard ${component.name} (${component.form_factor} → ${moboFormFactor}) fits in case with ${filterRequirements.formFactor} → ${caseFormFactor}, compatible with ${compatibleFormFactors.join(', ')}: ${isCompatible}`);
                
                return isCompatible;
              }
              
              // Case compatibility with motherboard form factor
              if (filterRequirements.formFactor && options === 'cases') {
                const moboFormFactor = normalizeFormFactor(filterRequirements.formFactor);
                const caseFormFactor = normalizeFormFactor(component.form_factor);
                
                // This case can fit the selected motherboard if the case form factor is compatible
                const caseCompatibleWith = formFactorCompatibility[caseFormFactor] || [caseFormFactor];
                const isCompatible = caseCompatibleWith.includes(moboFormFactor);
                
                console.log(`Checking if case ${component.name} (${component.form_factor} → ${caseFormFactor}) can fit motherboard with ${filterRequirements.formFactor} → ${moboFormFactor}: ${isCompatible}`);
                
                return isCompatible;
              }
              
              // GPU power requirements
              if (options === 'gpus' && filterRequirements.maxWattage) {
                const gpuWattage = parseInt(component.power_consumption) || 0;
                const maxWattage = parseInt(filterRequirements.maxWattage) || 0;
                return gpuWattage <= maxWattage;
              }
              
              // PSU wattage requirements
              if (options === 'psus' && filterRequirements.minWattage) {
                const psuWattage = parseInt(component.wattage) || 0;
                const minWattage = parseInt(filterRequirements.minWattage) || 0;
                return psuWattage >= minWattage;
              }
              
              return true;
            });
            
            console.log(`✅ ${options} filtering complete:`, {
              type: options,
              requirements: filterRequirements,
              beforeCount: data.length,
              afterCount: filteredData.length,
              filtered: data.length - filteredData.length,
            });
            
            // Debug log all filtered components
            if (filteredData.length === 0) {
              console.warn(`⚠️ No ${options} found after filtering with:`, filterRequirements);
            } else if (options === 'motherboards' || options === 'cases') {
              console.log(`🔧 Filtered ${options}:`, filteredData.map(item => ({
                name: item.name, 
                form_factor: item.form_factor,
                normalized: normalizeFormFactor(item.form_factor)
              })));
            }
          }
          
          // If no motherboards are found after filtering, show all with a warning
          if (options === 'motherboards' && filteredData.length === 0 && filterRequirements) {
            console.warn('⚠️ No compatible motherboards found! Showing all motherboards instead.');
            
            let errorMessage = '';
            
            // Special message for Socket 1851 (Intel Ultra) processors
            if (filterRequirements.socket && filterRequirements.socket.toLowerCase().includes('1851')) {
              errorMessage = `Hittade inga moderkort som är kompatibla med både Intel Ultra-processorn (Socket 1851) och detta chassi (${filterRequirements.formFactor}). Visar alla moderkort istället.`;
            } 
            // General message for form factor issues
            else if (filterRequirements.formFactor) {
              errorMessage = `Hittade inga moderkort som är kompatibla med detta chassi (${filterRequirements.formFactor}). Visar alla moderkort istället.`;
            }
            // General message for socket issues
            else if (filterRequirements.socket) {
              errorMessage = `Hittade inga moderkort som är kompatibla med denna processor (Socket ${filterRequirements.socket}). Visar alla moderkort istället.`;
            }
            
            if (errorMessage) {
              alert(errorMessage);
            }
            
            filteredData = data;
          }
          
          // Sort components by price (highest to lowest)
          filteredData = sortComponentsByPrice(filteredData);
          
          console.log('🎯 Final data being set:');
          console.log('  - Final filtered count:', filteredData.length);
          console.log('  - First 3 items:', filteredData.slice(0, 3));
          
          setComponents(filteredData);
          setChoices(filteredData);
          
          console.log('✅ Component state updated successfully');
          
        } catch (error) {
          console.error('❌ ERROR FETCHING COMPONENTS:');
          console.error('  - Component type:', options);
          console.error('  - API URL:', `${API_URL}/api/${options}`);
          console.error('  - Error type:', error.name);
          console.error('  - Error message:', error.message);
          console.error('  - Full error:', error);
          
          // Check if it's a network error
          if (error.name === 'TypeError' && error.message.includes('fetch')) {
            console.error('🌐 NETWORK ERROR: Cannot connect to backend API');
            console.error('  - Check if backend is running');
            console.error('  - Check if API_URL is correct:', API_URL);
            console.error('  - Check CORS settings');
          }
          
          // Check if it's a CORS error
          if (error.message.includes('CORS')) {
            console.error('🚫 CORS ERROR: Cross-origin request blocked');
            console.error('  - Backend needs to allow origin:', window.location.origin);
          }
          
          setComponents([]);
          setChoices([]);
        }
      };

      fetchComponents();
    }
  }, [options, filterRequirements]);

  // Function to sort components by price from highest to lowest
  const sortComponentsByPrice = (components) => {
    return [...components].sort((a, b) => {
      // Parse prices to integer values
      const priceA = typeof a.price === 'string' 
        ? parseInt(a.price.replace(/[^0-9]/g, ''), 10) || 0
        : a.price || 0;
      
      const priceB = typeof b.price === 'string'
        ? parseInt(b.price.replace(/[^0-9]/g, ''), 10) || 0
        : b.price || 0;
      
      // Sort from highest to lowest
      return priceB - priceA;
    });
  };

  const filteredChoices = search
    ? choices.filter((opt) =>
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
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          {img && <img src={img} alt={title} className="w-8 h-8" />}
          <h3 className="text-lg font-semibold">{title}</h3>
        </div>
        
        <button
          className="p-2 hover:bg-slate-300 rounded-full transition-colors"
          onClick={() => setShowGuide(true)}
        >
          <FiInfo className="w-5 h-5 text-gray-600" />
        </button>
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

      {/* Guide Modal */}
      {showGuide && (
        <div className="absolute top-0 right-0 mt-12 z-50">
          <div className="bg-white rounded-lg w-80 shadow-xl border border-gray-200">
            <div className="flex justify-between items-center border-b p-4">
              <h3 className="text-lg font-semibold">Guide: {title}</h3>
              <button
                onClick={() => setShowGuide(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <GuideContent type={options} />
          </div>
        </div>
      )}

      {/* Component Selection Modal */}
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
