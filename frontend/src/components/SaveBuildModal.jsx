import React, { useState } from 'react';

const SaveBuildModal = ({ isOpen, onClose, onSave }) => {
  const [buildName, setBuildName] = useState('');

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50">
      <div className="bg-slate-200 p-6 rounded-lg shadow-xl border-2 border-slate-400 max-w-md w-full mx-4">
        <h2 className="text-xl font-bold mb-4">Namnge din dator</h2>
        <form onSubmit={(e) => {
          e.preventDefault();
          onSave(buildName);
          setBuildName('');
        }}>
          <input
            type="text"
            value={buildName}
            onChange={(e) => setBuildName(e.target.value)}
            placeholder="T.ex. Gaming PC 2024"
            className="w-full p-2 border rounded mb-4"
            required
          />
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-slate-300 text-black hover:text-gray-700 hover:scale-105 border-2 hover:bg-slate-400 border-slate-600 rounded-lg shadow-lg"
            >
              Avbryt
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-slate-300 text-black hover:text-gray-700 hover:scale-105 border-2 hover:bg-slate-400 border-slate-600 rounded-lg shadow-lg"
            >
              Spara
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SaveBuildModal; 