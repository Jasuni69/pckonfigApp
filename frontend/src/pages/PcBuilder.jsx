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

const PcBuilder = () => {
  const [selectedComponents, setSelectedComponents] = useState({});
  const [compatibility, setCompatibility] = useState({
    socket: null,
    requiredWattage: 0,
    formFactor: null
  });

  const handleComponentSelect = (component, type) => {
    console.log(`Selected ${type}:`, component);
    
    // Clear dependent components when changing critical parts
    if (type === 'cpu') {
      setSelectedComponents(prev => ({
        ...prev,
        [type]: component,
        motherboard: null // Clear motherboard when CPU changes
      }));
    } else if (type === 'gpu') {
      setSelectedComponents(prev => ({
        ...prev,
        [type]: component,
        psu: null // Clear PSU when GPU changes
      }));
    } else {
      setSelectedComponents(prev => ({
        ...prev,
        [type]: component
      }));
    }

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
        if (selectedComponents.cpu) {
          console.log('Found CPU, creating motherboard filter with socket:', selectedComponents.cpu.socket);
          return { socket: selectedComponents.cpu.socket };
        }
        console.log('No CPU selected for motherboard filtering');
        return null;
        
      case 'cpus':
        if (selectedComponents.motherboard) {
          console.log('Found motherboard, creating CPU filter with socket:', selectedComponents.motherboard.socket);
          return { socket: selectedComponents.motherboard.socket };
        }
        console.log('No motherboard selected for CPU filtering');
        return null;
        
      case 'psus':  // Changed to match Card options prop
        return selectedComponents.gpu ? 
          { minWattage: selectedComponents.gpu.recommended_wattage } : null;
        
      case 'gpus':  // Changed to match Card options prop
        return selectedComponents.psu ? 
          { maxWattage: selectedComponents.psu.wattage } : null;
        
      case 'cases':  // Changed to match Card options prop
        return selectedComponents.motherboard ? 
          { formFactor: selectedComponents.motherboard.form_factor } : null;
        
      default:
        console.log('No filter requirements for type:', type);
        return null;
    }
  };

  const calculateTotal = () => {
    return Object.values(selectedComponents)
      .filter(component => component && component.price) // Add null check
      .reduce((total, component) => {
        const price = typeof component.price === 'string' 
          ? parseInt(component.price.replace(/[^0-9]/g, ''), 10) 
          : component.price;
        return total + (price || 0);
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

  return (
    <div className="wrapper bg-gradient-to-b from-slate-400 to-slate-200 pb-28 -mt-24">
      <div className="sticky top-28 z-10">
        <div className="flex justify-center items-center bg-slate-200 h-16 pt-16">
          <h1 className="flex text-2xl font-bold mt-96">Konfigurera din PC!</h1>
        </div>
        <div className="flex flex-col justify-center items-center min-h-screen pt-28">
          <div className="w-full max-w-7xl h-[50vh] grid grid-cols-5 grid-rows-6 gap-4 bg-slate-500 shadow-2xl border-2 border-slate-600 rounded-lg p-4">
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
              title="Strömförsörjning" 
              img={psuIcon} 
              className="row-span-3 col-start-3 row-start-4" 
              options="psus"
              onSelect={(component) => handleComponentSelect(component, 'psu')} 
            />
            <Card 
              title="Extra" 
              className="row-span-3 col-start-5 row-start-4" 
              options="extras"
              onSelect={(component) => handleComponentSelect(component, 'extra')} 
            />
            <Card 
              title="Användningsområde" 
              className="row-span-3 col-start-4 row-start-4" 
              options="purpose" 
              onSelect={(component) => handleComponentSelect(component, 'purpose')} 
            />
          </div>
        </div>

        <div className="flex justify-center -mt-40">
          <div className="w-full max-w-7xl bg-slate-300 rounded-lg shadow-lg border-2 border-slate-800 p-6">
            <h2 className="text-xl font-bold mb-4">Valda komponenter</h2>
            <div className="space-y-2">
              {Object.entries(selectedComponents)
                .filter(([_, comp]) => comp !== null && comp !== undefined)  // Filter out null/undefined
                .map(([type, comp]) => (
                  <div key={type} className="flex justify-between items-center p-2 bg-slate-200 rounded">
                    <span>{componentLabels[type]}: {comp.name}</span>
                    <span>{comp.price ? `${comp.price} kr` : ''}</span>
                  </div>
                ))}
            </div>
            <div className="mt-4 pt-4 border-t-2 border-slate-400">
              <div className="flex justify-between items-center font-bold text-lg">
                <span>Totalt:</span>
                <span>{calculateTotal()} kr</span>
                <div className="flex justify-center items-center gap-4">
                  <button className="bg-slate-300 text-black hover:text-gray-700 hover:scale-105 border-2 hover:bg-slate-400 border-slate-600 rounded-lg p-1 shadow-lg">Spara dator</button>
                  <button className="bg-slate-300 text-black hover:text-gray-700 hover:scale-105 border-2 hover:bg-slate-400 border-slate-600 rounded-lg p-1 shadow-lg">Optimera dator</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PcBuilder;
