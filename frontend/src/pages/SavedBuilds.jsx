import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { X } from "lucide-react";

const BuildCard = ({ build, onDelete }) => {
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();

  return (
    <div className="bg-slate-200 rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-lg font-semibold">{build.name}</h3>
      </div>
      
      <div
        className="bg-slate-300 shadow-md p-6 cursor-pointer hover:bg-slate-400 transition-colors"
        onClick={() => setIsOpen(true)}
      >
        <div className="flex justify-between items-center">
          <span>{build.name}</span>
          <span>
            {Object.values(build)
              .filter(comp => comp && typeof comp === 'object' && comp.price)
              .reduce((total, comp) => total + comp.price, 0)} kr
          </span>
        </div>
      </div>

      {/* Details Modal */}
      {isOpen && (
        <div className="fixed inset-0 flex items-center justify-center z-50">
          <div
            className="bg-slate-400 p-8 rounded-lg border-2 border-slate-800 shadow-lg w-96 max-w-[90vw]"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-black">{build.name}</h2>
              <button
                className="bg-slate-300 rounded-lg p-2 border-2 border-slate-800 shadow-lg hover:bg-slate-400 transition-colors"
                onClick={() => setIsOpen(false)}
              >
                <X className="h-5 w-5 text-black hover:scale-105" />
              </button>
            </div>

            {/* Build Details */}
            <div className="bg-white border border-gray-300 rounded shadow-lg max-h-[60vh] overflow-y-auto">
              <ul>
                {build.cpu && (
                  <li className="p-4 border-b border-gray-100 flex justify-between items-center">
                    <span>Processor</span>
                    <span>{build.cpu.name}</span>
                  </li>
                )}
                {build.gpu && (
                  <li className="p-4 border-b border-gray-100 flex justify-between items-center">
                    <span>Grafikkort</span>
                    <span>{build.gpu.name}</span>
                  </li>
                )}
                {build.motherboard && (
                  <li className="p-4 border-b border-gray-100 flex justify-between items-center">
                    <span>Moderkort</span>
                    <span>{build.motherboard.name}</span>
                  </li>
                )}
                {build.ram && (
                  <li className="p-4 border-b border-gray-100 flex justify-between items-center">
                    <span>RAM</span>
                    <span>{build.ram.name}</span>
                  </li>
                )}
                {build.storage && (
                  <li className="p-4 border-b border-gray-100 flex justify-between items-center">
                    <span>Lagring</span>
                    <span>{build.storage.name}</span>
                  </li>
                )}
                {build.case && (
                  <li className="p-4 border-b border-gray-100 flex justify-between items-center">
                    <span>Chassi</span>
                    <span>{build.case.name}</span>
                  </li>
                )}
                {build.psu && (
                  <li className="p-4 border-b border-gray-100 flex justify-between items-center">
                    <span>Nätaggregat</span>
                    <span>{build.psu.name}</span>
                  </li>
                )}
                {build.cooler && (
                  <li className="p-4 border-b border-gray-100 flex justify-between items-center">
                    <span>CPU-Kylare</span>
                    <span>{build.cooler.name}</span>
                  </li>
                )}
              </ul>

              <div className="p-4 border-t border-gray-300 flex justify-between items-center bg-gray-50">
                <span className="font-bold">Total:</span>
                <span className="font-bold">
                  {Object.values(build)
                    .filter(comp => comp && typeof comp === 'object' && comp.price)
                    .reduce((total, comp) => total + comp.price, 0)} kr
                </span>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="mt-4 flex justify-end space-x-2">
              <button
                onClick={() => {
                  onDelete(build.id);
                  setIsOpen(false);
                }}
                className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
              >
                Ta bort
              </button>
              <button
                onClick={() => navigate(`/pcbuilder?build=${build.id}`)}
                className="bg-slate-300 text-black px-4 py-2 rounded hover:bg-slate-400"
              >
                Redigera
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const SavedBuilds = () => {
  const [builds, setBuilds] = useState([]);
  const [loading, setLoading] = useState(true);
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    fetchBuilds();
  }, [isAuthenticated]);

  const fetchBuilds = async () => {
    try {
      const response = await fetch('http://13.53.243.200/api/builds', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) throw new Error('Failed to fetch builds');
      
      const data = await response.json();
      setBuilds(data);
    } catch (error) {
      console.error('Error fetching builds:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (buildId) => {
    if (!window.confirm('Är du säker på att du vill ta bort denna build?')) return;

    try {
      const response = await fetch(`http://13.53.243.200/api/builds/${buildId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) throw new Error('Failed to delete build');
      
      setBuilds(builds.filter(build => build.id !== buildId));
    } catch (error) {
      console.error('Error deleting build:', error);
      alert('Kunde inte ta bort bygget. Försök igen senare.');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-400 to-slate-200 pt-28 px-4">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold mb-6">Laddar sparade byggen...</h1>
        </div>
      </div>
    );
  }

  return (
    <div className="wrapper bg-gradient-to-b from-slate-400 to-slate-200 pb-28 -mt-24">
      <div className="sticky top-28 z-10">
        <div className="flex justify-center items-center bg-slate-200 h-16 pt-16">
          <h1 className="flex text-2xl font-bold mt-96 text-slate-800">Mina Sparade Byggen</h1>
        </div>
        
        <div className="flex flex-col justify-center items-center min-h-screen pt-28">
          <div className="w-full max-w-7xl grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 bg-slate-500 shadow-2xl border-2 border-slate-400 rounded-lg p-4">
            {builds.length === 0 ? (
              <div className="col-span-full bg-slate-300 rounded-lg p-6 text-center">
                <p>Du har inga sparade byggen än.</p>
                <button 
                  onClick={() => navigate('/pcbuilder')}
                  className="mt-4 bg-slate-400 text-black hover:text-gray-700 hover:scale-105 border-2 hover:bg-slate-500 border-slate-600 rounded-lg p-2 shadow-lg"
                >
                  Skapa din första PC
                </button>
              </div>
            ) : (
              builds.map(build => (
                <BuildCard 
                  key={build.id} 
                  build={build} 
                  onDelete={handleDelete}
                />
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SavedBuilds; 