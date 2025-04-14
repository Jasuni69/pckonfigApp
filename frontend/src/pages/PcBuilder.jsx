import { useState } from 'react';
import Card from '../components/Card';
import caseIcon from '../assets/icons/case.svg';
import motherboardIcon from '../assets/icons/motherboard.svg';
import cpuIcon from '../assets/icons/cpu.svg';
import ramIcon from '../assets/icons/ram.svg';
import gpuIcon from '../assets/icons/gpu.svg';
import hddIcon from '../assets/icons/hdd.svg';
import cpuCoolerIcon from '../assets/icons/cpu-cooler.svg';
import psuIcon from '../assets/icons/psu.svg';  
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import SaveBuildModal from '../components/SaveBuildModal';
import { API_URL } from '../config';
import OptimizationResultsModal from '../components/OptimizationResultsModal';
import Layout from '../components/Layout';

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
  return ff;
};

const formFactorCompatibility = {
  "ssi-eeb": ["ssi-eeb", "e-atx", "atx", "micro-atx", "mini-itx"],
  "e-atx": ["e-atx", "atx", "micro-atx", "mini-itx"],
  "atx": ["atx", "micro-atx", "mini-itx"],
  "micro-atx": ["micro-atx", "mini-itx"],
  "mini-itx": ["mini-itx"]
};

const PcBuilder = () => {
  const [selectedComponents, setSelectedComponents] = useState({});
  const [compatibility, setCompatibility] = useState({
    socket: null,
    requiredWattage: 0,
    formFactor: null
  });
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [isSaving, setIsSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [showOptimizationModal, setShowOptimizationModal] = useState(false);
  const [optimizationData, setOptimizationData] = useState(null);

  const handleComponentSelect = (component, type) => {
    console.log(`Selected ${type}:`, component);
    if (!component) return;
    
    setSelectedComponents(prev => ({
      ...prev,
      [type]: component
    }));

    // Update compatibility requirements
    switch(type) {
      case 'cpu':
        setCompatibility(prev => ({ 
          ...prev, 
          socket: component.socket 
        }));
        break;
      case 'motherboard':
        setCompatibility(prev => ({ 
          ...prev, 
          socket: component.socket,
          formFactor: component.form_factor
        }));
        break;
      case 'gpu':
        setCompatibility(prev => ({ 
          ...prev, 
          requiredWattage: component.recommended_wattage 
        }));
        break;
      case 'psu':
        // No compatibility updates needed for PSU
        break;
    }
  };

  const getFilterRequirements = (type) => {
    console.log('Getting filter requirements for:', type);
    
    switch(type) {
      case 'motherboards':
        const requirements = {};
        
        if (selectedComponents.cpu) {
          requirements.socket = selectedComponents.cpu.socket;
          console.log('Found CPU, adding socket requirement:', selectedComponents.cpu.socket);
          
          // Special case for Intel Ultra (Socket 1851)
          if (requirements.socket && requirements.socket.toLowerCase().includes('1851')) {
            console.log('Intel Ultra processor detected (Socket 1851) - requires specific motherboards');
          }
        }
        
        if (selectedComponents.case) {
          // Add the raw form factor directly
          requirements.formFactor = selectedComponents.case.form_factor;
          const normalizedFF = normalizeFormFactor(requirements.formFactor);
          
          console.log('Found case, adding form factor requirement:', {
            original: requirements.formFactor,
            normalized: normalizedFF,
            supportedSizes: formFactorCompatibility[normalizedFF] || [normalizedFF]
          });
        }
        
        if (Object.keys(requirements).length > 0) {
          console.log('Motherboard filter requirements:', requirements);
          return requirements;
        }
        
        console.log('No requirements for motherboard filtering');
        return null;
        
      case 'cpus':
        if (selectedComponents.motherboard) {
          const socket = selectedComponents.motherboard.socket;
          console.log('Found motherboard, creating CPU filter with socket:', socket);
          
          // Special case for Socket 1851 motherboards - they need exact matches
          if (socket && socket.toLowerCase().includes('1851')) {
            console.log('Socket 1851 motherboard detected - requires Intel Ultra processors');
            return { socket: socket };
          }
          
          return { socket: socket };
        }
        console.log('No motherboard selected for CPU filtering');
        return null;
        
      case 'psus':
        if (selectedComponents.gpu) {
          const minWattage = selectedComponents.gpu.recommended_wattage;
          console.log('PSU filter requirements:', {
            gpu: selectedComponents.gpu.name,
            recommendedWattage: minWattage
          });
          return { minWattage };
        }
        return null;
        
      case 'gpus':
        if (selectedComponents.psu) {
          const maxWattage = selectedComponents.psu.wattage;
          console.log('GPU filter requirements:', {
            psu: selectedComponents.psu.name,
            availableWattage: maxWattage
          });
          return { maxWattage };
        }
        return null;
        
      case 'cases':
        if (selectedComponents.motherboard) {
          // Add the raw form factor directly
          const formFactor = selectedComponents.motherboard.form_factor;
          const normalizedFF = normalizeFormFactor(formFactor);
          
          console.log('Case filter requirements:', {
            motherboard: selectedComponents.motherboard.name,
            original: formFactor,
            normalized: normalizedFF
          });
          
          return { formFactor };
        }
        console.log('No motherboard selected for case filtering');
        return null;
        
      default:
        console.log('No filter requirements for type:', type);
        return null;
    }
  };

  const calculateTotal = () => {
    return Object.values(selectedComponents)
      .filter(component => component && typeof component === 'object' && component.price)
      .reduce((total, component) => {
        const price = typeof component.price === 'string' 
          ? parseInt(component.price.replace(/[^0-9]/g, ''), 10) 
          : component.price;
        return total + (Number.isFinite(price) ? price : 0);
      }, 0);
  };

  // Map English keys to Swedish labels
  const componentLabels = {
    case: "Chassi",
    motherboard: "Moderkort",
    cpu: "Processor",
    ram: "Ram-Minne",
    gpu: "Grafikkort",
    hdd: "Hårddisk",
    "cpu-cooler": "CPU-Kylare",
    psu: "Strömförsörjning",
    extra: "Extra",
    purpose: "Användningsområde",
  };

  const handleSave = async (buildName) => {
    try {
      // Validate input
      if (!buildName.trim()) {
        alert('Du måste ange ett namn för din dator');
        return;
      }
      
      // Check if there are any components selected
      if (Object.keys(selectedComponents).filter(key => key !== 'purpose').length === 0) {
        alert('Välj minst en komponent innan du sparar');
        setShowSaveModal(false);
        return;
      }
      
      setIsSaving(true);
      const buildData = {
        name: buildName.trim(),
        purpose: selectedComponents.purpose?.name || selectedComponents.purpose || null,
        cpu_id: selectedComponents.cpu?.id || null,
        gpu_id: selectedComponents.gpu?.id || null,
        motherboard_id: selectedComponents.motherboard?.id || null,
        ram_id: selectedComponents.ram?.id || null,
        psu_id: selectedComponents.psu?.id || null,
        case_id: selectedComponents.case?.id || null,
        storage_id: selectedComponents.hdd?.id || null,
        cooler_id: selectedComponents['cpu-cooler']?.id || null,
        is_published: false
      };

      console.log('Saving build data:', buildData);

      const response = await fetch(`${API_URL}/api/builds`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(buildData)
      });

      // Try to get detailed error information if available
      const responseData = await response.json().catch(() => null);
      
      if (!response.ok) {
        console.error('Failed to save build:', response.status, responseData);
        throw new Error(`Failed to save build: ${response.status} - ${responseData?.detail || 'Unknown error'}`);
      }

      alert('Din dator har sparats!');
      setShowSaveModal(false);
    } catch (error) {
      console.error('Error saving build:', error);
      alert(`Kunde inte spara datorn: ${error.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleOptimize = async () => {
    if (!isAuthenticated) {
      if (window.confirm('Du måste logga in för att använda denna funktion. Vill du logga in nu?')) {
        navigate('/login');
      }
      return;
    }

    const authToken = localStorage.getItem('token');
    
    if (!authToken) {
      alert('Du måste logga in igen för att fortsätta.');
      navigate('/login');
      return;
    }

    if (!selectedComponents.purpose || !selectedComponents.purpose.name) {
      alert("Välj ett användningsområde innan du optimerar din bygg.");
      return;
    }

    // Check that we have at least CPU or GPU selected
    if (!selectedComponents.cpu && !selectedComponents.gpu) {
      alert("Välj minst en CPU eller GPU innan du optimerar din bygg.");
      return;
    }

    setIsLoading(true);

    try {
      // Create payload with all component IDs
      const payload = {
        cpu_id: selectedComponents.cpu?.id,
        gpu_id: selectedComponents.gpu?.id,
        motherboard_id: selectedComponents.motherboard?.id,
        ram_id: selectedComponents.ram?.id,
        psu_id: selectedComponents.psu?.id,
        case_id: selectedComponents.case?.id,
        storage_id: selectedComponents.hdd?.id,
        cooler_id: selectedComponents['cpu-cooler']?.id,
        purpose: selectedComponents.purpose?.name || "general use"
      }

      console.log('Sending optimization request:', payload);
      
      const response = await fetch(`${API_URL}/api/optimize/build`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      console.log('API response status:', response.status);
      
      if (response.status === 401) {
        throw new Error('Din inloggning har upphört. Logga in igen för att fortsätta.');
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        console.error('Failed to optimize PC:', response.status, errorData);
        alert(`Ett fel uppstod under optimering: ${errorData.detail || response.statusText}. Försök igen senare eller välj komponenter manuellt.`);
        return;
      }

      const data = await response.json();
      console.log('Optimization response:', data);
      
      // Show the explanation in a modal
      setOptimizationData(data);
      setShowOptimizationModal(true);
    } catch (error) {
      console.error('Failed to optimize PC:', error);
      
      if (error.message.includes('inloggning har upphört')) {
        alert(error.message);
        navigate('/login');
      } else {
        alert(`Ett tekniskt fel uppstod: ${error.message}. Försök igen senare eller välj komponenter manuellt.`);
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Add handleApplyRecommendations function
  const handleApplyRecommendations = (recommendations) => {
    console.log('Applying recommendations to build:', recommendations);
    
    // Create a new components object with the recommendations
    const updatedComponents = { ...selectedComponents };
    
    // Update each component if it exists in recommendations
    if (recommendations.cpu) {
      updatedComponents.cpu = recommendations.cpu;
    }
    
    if (recommendations.gpu) {
      updatedComponents.gpu = recommendations.gpu;
    }
    
    if (recommendations.motherboard) {
      updatedComponents.motherboard = recommendations.motherboard;
    }
    
    if (recommendations.ram) {
      updatedComponents.ram = recommendations.ram;
    }
    
    if (recommendations.psu) {
      updatedComponents.psu = recommendations.psu;
    }
    
    if (recommendations.case) {
      updatedComponents.case = recommendations.case;
    }
    
    if (recommendations.storage) {
      updatedComponents.hdd = recommendations.storage;
    }
    
    if (recommendations.cooler) {
      updatedComponents['cpu-cooler'] = recommendations.cooler;
    }
    
    // Update compatibility state based on new components
    let newCompatibility = { ...compatibility };
    
    if (recommendations.cpu) {
      newCompatibility.socket = recommendations.cpu.socket;
    }
    
    if (recommendations.motherboard) {
      newCompatibility.socket = recommendations.motherboard.socket;
      newCompatibility.formFactor = recommendations.motherboard.form_factor;
    }
    
    if (recommendations.gpu) {
      newCompatibility.requiredWattage = recommendations.gpu.recommended_wattage;
    }
    
    // Update state
    setSelectedComponents(updatedComponents);
    setCompatibility(newCompatibility);
    
    // Show a confirmation message
    alert('Rekommenderade komponenter har applicerats på din byggkonfiguration!');
  };

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-slate-800 text-center mb-12">
          Konfigurera Din PC
        </h1>

        {/* Component Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <Card 
            title="Chassi" 
            img={caseIcon} 
            className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow" 
            options="cases"
            onSelect={(component) => handleComponentSelect(component, 'case')}
            filterRequirements={getFilterRequirements('cases')}
          />
          <Card 
            title="Moderkort" 
            img={motherboardIcon} 
            className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow row-start-2 col-start-1" 
            options="motherboards"
            onSelect={(component) => handleComponentSelect(component, 'motherboard')} 
            filterRequirements={getFilterRequirements('motherboards')}
          />
          <Card 
            title="Processor" 
            img={cpuIcon} 
            className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow row-start-2 col-start-2" 
            options="cpus"
            onSelect={(component) => handleComponentSelect(component, 'cpu')} 
            filterRequirements={getFilterRequirements('cpus')}
          />
          <Card 
            title="Ram-Minne" 
            img={ramIcon} 
            className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow row-start-2 col-start-3" 
            options="ram"
            onSelect={(component) => handleComponentSelect(component, 'ram')} 
          />
          <Card 
            title="Grafikkort" 
            img={gpuIcon} 
            className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow row-start-2 col-start-4" 
            options="gpus"
            onSelect={(component) => handleComponentSelect(component, 'gpu')} 
            filterRequirements={getFilterRequirements('gpus')}
          />
          <Card 
            title="Hårddisk" 
            img={hddIcon} 
            className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow row-start-3 col-start-1" 
            options="storage"
            onSelect={(component) => handleComponentSelect(component, 'hdd')} 
          />
          <Card 
            title="CPU-Kylare" 
            img={cpuCoolerIcon} 
            className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow row-start-3 col-start-2" 
            options="coolers"
            onSelect={(component) => handleComponentSelect(component, 'cpu-cooler')} 
          />
          <Card 
            title="Nätaggregat" 
            img={psuIcon} 
            className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow row-start-3 col-start-3" 
            options="psus"
            onSelect={(component) => handleComponentSelect(component, 'psu')} 
            filterRequirements={getFilterRequirements('psus')}
          />
          <Card 
            title="Extra" 
            className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow row-start-3 col-start-4" 
            options="extras"
            onSelect={(component) => handleComponentSelect(component, 'extra')} 
          />
          <Card 
            title="Användning" 
            className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow row-start-4 col-start-1" 
            options="purpose" 
            onSelect={(component) => handleComponentSelect(component, 'purpose')} 
          />
        </div>

        {/* Summary Panel */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-2xl font-bold mb-6">Valda Komponenter</h2>
          <div className="space-y-4 mb-6">
            {Object.entries(selectedComponents)
              .filter(([_, comp]) => comp && typeof comp === 'object' && comp.name)
              .map(([type, comp]) => (
                <div key={type} className="flex justify-between items-center p-2 bg-slate-200 rounded">
                  <span>{componentLabels[type] || type}: {comp.name}</span>
                  <span>{comp.price ? `${comp.price} kr` : ''}</span>
                </div>
              ))}
          </div>

          {/* Total and Actions */}
          <div className="flex items-center justify-between pt-6 border-t">
            <div className="text-2xl font-bold">
              Totalt: {calculateTotal()} kr
            </div>
            <div className="flex gap-4">
              <button 
                onClick={() => setShowSaveModal(true)}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Spara Bygg
              </button>
              <button 
                onClick={handleOptimize}
                className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors"
              >
                Optimera
              </button>
            </div>
          </div>
        </div>
      </div>

      <SaveBuildModal
        isOpen={showSaveModal}
        onClose={() => setShowSaveModal(false)}
        onSave={handleSave}
      />

      <OptimizationResultsModal
        isOpen={showOptimizationModal}
        onClose={() => setShowOptimizationModal(false)}
        optimizationResult={optimizationData}
        onApplyRecommendations={handleApplyRecommendations}
      />
    </Layout>
  );
};

export default PcBuilder;

