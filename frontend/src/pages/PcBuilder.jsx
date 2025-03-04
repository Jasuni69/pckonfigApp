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
    formFactor: null,
  });

  const handleComponentSelect = (component, type) => {
    setSelectedComponents(prev => ({
      ...prev,
      [type]: component,
    }));

    // Update compatibility requirements
    if (type === 'cpu') {
      setCompatibility(prev => ({ ...prev, socket: component.socket }));
    }
    if (type === 'gpu') {
      setCompatibility(prev => ({ ...prev, requiredWattage: component.recommended_wattage }));
    }
    if (type === 'motherboard') {
      setCompatibility(prev => ({ 
        ...prev, 
        socket: component.socket,
        formFactor: component.form_factor 
      }));
    }
  };

  const getFilterRequirements = (type) => {
    switch(type) {
      case 'motherboard':
        return { 
          socket: compatibility.socket,
          // If case is selected, check form factor compatibility
          formFactor: selectedComponents.case ? selectedComponents.case.form_factor : null
        };
      case 'cpu':
        return { socket: selectedComponents.motherboard?.socket };
      case 'psu':
        return { minWattage: compatibility.requiredWattage };
      case 'case':
        return { 
          // If motherboard is selected, ensure case supports its form factor
          formFactor: compatibility.formFactor 
        };
      default:
        return null;
    }
  };

  const calculateTotal = () => {
    return Object.values(selectedComponents).reduce((sum, comp) => sum + Number(comp.price), 0);
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
            />
            <Card 
              title="Processor" 
              img={cpuIcon} 
              className="row-span-3 col-start-3 row-start-1" 
              options="cpus"
              onSelect={(component) => handleComponentSelect(component, 'cpu')} 
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
              {Object.entries(selectedComponents).map(([type, comp]) => (
                <div key={type} className="flex justify-between items-center p-2 bg-slate-200 rounded">
                  <span>{componentLabels[type]}: {comp.name}</span>
                  <span>{comp.price} kr</span>
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
