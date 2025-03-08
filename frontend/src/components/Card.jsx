import { useState, useEffect } from "react";
import { X } from "lucide-react";
import { FiInfo } from 'react-icons/fi';

const normalizeFormFactor = (formFactor) => {
  if (!formFactor) return '';
  
  const ff = formFactor.toLowerCase();
  
  // Handle common variations and Swedish translations
  if (ff.includes('utökad') || ff.includes('extended') || ff.includes('e-atx')) return 'e-atx';
  if (ff.includes('micro')) return 'micro-atx';
  if (ff.includes('mini-mini')) return 'mini-itx'; // Handle double "mini" case
  if (ff.includes('mini')) return 'mini-itx';
  if (ff === 'atx') return 'atx';
  
  // Log unexpected form factors
  console.log('Unexpected form factor:', formFactor);
  return ff;
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
              <li>- LGA 1700: 12:e/13:e gen</li>
              <li>- LGA 1200: 10:e/11:e gen</li>
            </ul>
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

  const filteredChoices = search
    ? choices.filter((opt) =>
        opt.name.toLowerCase().includes(search.toLowerCase())
      )
    : choices;

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
