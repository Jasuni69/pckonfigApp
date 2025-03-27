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

const formFactorCompatibility = {
  "Utökad ATX": ["Utökad ATX", "ATX", "Micro ATX", "Mini ITX"],
  "ATX": ["ATX", "Micro ATX", "Mini ITX"],
  "Micro ATX": ["Micro ATX", "Mini ITX"],
  "Mini ITX": ["Mini ITX"]
};

const PcBuilder = () => {
  const [selectedComponents, setSelectedComponents] = useState({});
  const [compatibility, setCompatibility] = useState({
    socket: null,
    requiredWattage: 0,
    formFactor: null
  });
  const { isAuthenticated, token } = useAuth();
  const navigate = useNavigate();
  const [isSaving, setIsSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [showSaveModal, setShowSaveModal] = useState(false);

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
        }
        
        if (selectedComponents.case) {
          const caseFormFactor = selectedComponents.case.form_factor;
          requirements.compatibleFormFactors = formFactorCompatibility[caseFormFactor] || [caseFormFactor];
          console.log('Found case, adding compatible form factors:', requirements.compatibleFormFactors);
        }
        
        if (Object.keys(requirements).length > 0) {
          console.log('Motherboard filter requirements:', requirements);
          return requirements;
        }
        
        console.log('No requirements for motherboard filtering');
        return null;
        
      case 'cpus':
        if (selectedComponents.motherboard) {
          console.log('Found motherboard, creating CPU filter with socket:', selectedComponents.motherboard.socket);
          return { socket: selectedComponents.motherboard.socket };
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
          const formFactor = selectedComponents.motherboard.form_factor;
          console.log('Case filter requirements:', {
            motherboard: selectedComponents.motherboard.name,
            formFactor: formFactor
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

  const handleAuthenticatedAction = async (action) => {
    if (!isAuthenticated) {
      if (window.confirm('Du måste logga in för att använda denna funktion. Vill du logga in nu?')) {
        navigate('/login');
      }
      return;
    }

    if (action === 'save') {
      try {
        setIsSaving(true);
        
        // Check if there are any components selected
        if (Object.keys(selectedComponents).length === 0) {
          alert('Välj minst en komponent innan du sparar');
          return;
        }

        const buildData = {
          name: "Min PC Build",
          cpu_id: selectedComponents.cpu?.id || null,
          gpu_id: selectedComponents.gpu?.id || null,
          motherboard_id: selectedComponents.motherboard?.id || null,
          ram_id: selectedComponents.ram?.id || null,
          psu_id: selectedComponents.psu?.id || null,
          case_id: selectedComponents.case?.id || null,
          storage_id: selectedComponents.hdd?.id || null,
          cooler_id: selectedComponents['cpu-cooler']?.id || null
        };

        const response = await fetch('http://16.16.99.193/api/builds', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(buildData)
        });

        if (!response.ok) {
          throw new Error('Failed to save build');
        }

        alert('Din dator har sparats!');
      } catch (error) {
        console.error('Error saving build:', error);
        alert('Kunde inte spara datorn. Försök igen senare.');
      } finally {
        setIsSaving(false);
      }
    }
  };

  const handleSave = async (buildName) => {
    try {
      setIsSaving(true);
      const buildData = {
        name: buildName,
        purpose: selectedComponents.purpose?.name || null,
        cpu_id: selectedComponents.cpu?.id || null,
        gpu_id: selectedComponents.gpu?.id || null,
        motherboard_id: selectedComponents.motherboard?.id || null,
        ram_id: selectedComponents.ram?.id || null,
        psu_id: selectedComponents.psu?.id || null,
        case_id: selectedComponents.case?.id || null,
        storage_id: selectedComponents.hdd?.id || null,
        cooler_id: selectedComponents['cpu-cooler']?.id || null
      };

      console.log('Saving build data:', buildData);

      const response = await fetch('http://16.16.99.193/api/builds', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(buildData)
      });

      if (!response.ok) {
        throw new Error('Failed to save build');
      }

      alert('Din dator har sparats!');
      setShowSaveModal(false);
    } catch (error) {
      console.error('Error saving build:', error);
      alert('Kunde inte spara datorn. Försök igen senare.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleOptimizePC = async () => {
    if (!isAuthenticated) {
      if (window.confirm('Du måste logga in för att använda denna funktion. Vill du logga in nu?')) {
        navigate('/login');
      }
      return;
    }

    try {
      setIsLoading(true);
      
      // Using the updated endpoint path
      const response = await fetch('http://16.16.99.193/api/optimize/build', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          cpu_id: selectedComponents.cpu?.id,
          gpu_id: selectedComponents.gpu?.id,
          motherboard_id: selectedComponents.motherboard?.id,
          ram_id: selectedComponents.ram?.id,
          psu_id: selectedComponents.psu?.id,
          case_id: selectedComponents.case?.id,
          storage_id: selectedComponents.hdd?.id,
          cooler_id: selectedComponents['cpu-cooler']?.id,
          purpose: selectedComponents.purpose?.name || "general use"
        })
      });

      if (!response.ok) {
        throw new Error('Failed to optimize PC');
      }

      const data = await response.json();
      console.log('Optimization response:', data);
      
      // Just show the explanation
      if (data && data.explanation) {
        alert(`Optimeringsförslag:\n\n${data.explanation}`);
      } else {
        alert('Din dator har optimerats!');
      }
    } catch (error) {
      console.error('Failed to optimize PC:', error);
      alert('Kunde inte optimera datorn. Försök igen senare.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="wrapper bg-gradient-to-b from-slate-400 to-slate-200 pb-28 -mt-24">
      <div className="sticky top-28 z-10">
        <div className="flex justify-center items-center bg-slate-200 h-16 pt-16">
          <h1 className="flex text-2xl font-bold mt-96 text-slate-800">Konfigurera din PC!</h1>
        </div>
        <div className="flex flex-col justify-center items-center min-h-screen pt-28">
          <div className="w-full max-w-7xl h-[50vh] grid grid-cols-5 grid-rows-6 gap-4 bg-slate-500 shadow-2xl border-2 border-slate-400 rounded-lg p-4">
            <Card 
              title="Chassi" 
              img={caseIcon} 
              className="row-span-3" 
              options="cases"
              onSelect={(component) => handleComponentSelect(component, 'case')}
              filterRequirements={getFilterRequirements('case')}
            />
            <Card 
              title="Moderkort" 
              img={motherboardIcon} 
              className="row-span-3 col-start-2 row-start-1" 
              options="motherboards"
              onSelect={(component) => handleComponentSelect(component, 'motherboard')} 
              filterRequirements={getFilterRequirements('motherboards')}
            />
            <Card 
              title="Processor" 
              img={cpuIcon} 
              className="row-span-3 col-start-3 row-start-1" 
              options="cpus"
              onSelect={(component) => handleComponentSelect(component, 'cpu')} 
              filterRequirements={getFilterRequirements('cpus')}
            />
            <Card 
              title="Ram-Minne" 
              img={ramIcon} 
              className="row-span-3 col-start-4 row-start-1" 
              options="ram"
              onSelect={(component) => handleComponentSelect(component, 'ram')} 
            />
            <Card 
              title="Grafikkort" 
              img={gpuIcon} 
              className="row-span-3 col-start-5 row-start-1" 
              options="gpus"
              onSelect={(component) => handleComponentSelect(component, 'gpu')} 
              filterRequirements={getFilterRequirements('gpus')}
            />
            <Card 
              title="Hårddisk" 
              img={hddIcon} 
              className="row-span-3 col-start-1 row-start-4" 
              options="storage"
              onSelect={(component) => handleComponentSelect(component, 'hdd')} 
            />
            <Card 
              title="CPU-Kylare" 
              img={cpuCoolerIcon} 
              className="row-span-3 col-start-2 row-start-4" 
              options="coolers"
              onSelect={(component) => handleComponentSelect(component, 'cpu-cooler')} 
            />
            <Card 
              title="Nätaggregat" 
              img={psuIcon} 
              className="row-span-3 col-start-3 row-start-4" 
              options="psus"
              onSelect={(component) => handleComponentSelect(component, 'psu')} 
              filterRequirements={getFilterRequirements('psus')}
            />
            <Card 
              title="Extra" 
              className="row-span-3 col-start-5 row-start-4" 
              options="extras"
              onSelect={(component) => handleComponentSelect(component, 'extra')} 
            />
            <Card 
              title="Användning" 
              className="row-span-3 col-start-4 row-start-4" 
              options="purpose" 
              onSelect={(component) => handleComponentSelect(component, 'purpose')} 
            />
          </div>
        </div>

        <div className="flex justify-center -mt-40">
          <div className="w-full max-w-7xl bg-slate-300 rounded-lg shadow-lg border-2 border-slate-400 p-6">
            <h2 className="text-xl font-bold mb-4">Valda komponenter</h2>
            <div className="space-y-2">
              {Object.entries(selectedComponents)
                .filter(([_, comp]) => comp && typeof comp === 'object' && comp.name)
                .map(([type, comp]) => (
                  <div key={type} className="flex justify-between items-center p-2 bg-slate-200 rounded">
                    <span>{componentLabels[type] || type}: {comp.name}</span>
                    <span>{comp.price ? `${comp.price} kr` : ''}</span>
                  </div>
                ))}
            </div>
            <div className="mt-4 pt-4 border-t-2 border-slate-400">
              <div className="flex justify-between items-center font-bold text-lg">
                <span>Totalt:</span>
                <span>{calculateTotal()} kr</span>
                <div className="flex justify-center items-center gap-4">
                  <button 
                    onClick={() => {
                      if (!isAuthenticated) {
                        if (window.confirm('Du måste logga in för att spara din dator. Vill du logga in nu?')) {
                          navigate('/login');
                        }
                        return;
                      }
                      setShowSaveModal(true);
                    }}
                    disabled={isSaving}
                    className="bg-slate-300 text-black hover:text-gray-700 hover:scale-105 border-2 hover:bg-slate-400 border-slate-600 rounded-lg p-1 shadow-lg"
                  >
                    {isSaving ? 'Sparar...' : 'Spara dator'}
                  </button>
                  <button 
                    onClick={handleOptimizePC}
                    disabled={isLoading}
                    className="bg-slate-300 text-black hover:text-gray-700 hover:scale-105 border-2 hover:bg-slate-400 border-slate-600 rounded-lg p-1 shadow-lg"
                  >
                    {isLoading ? 'Optimerar...' : 'Optimera dator'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <SaveBuildModal
        isOpen={showSaveModal}
        onClose={() => setShowSaveModal(false)}
        onSave={handleSave}
      />
    </div>
  );
};

export default PcBuilder;
