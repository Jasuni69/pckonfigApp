import React from "react";

const CreateAccount = () => {
  return (
    <div className="wrapper bg-gradient-to-b from-slate-400 to-slate-200">
      <div className="min-h-screen flex flex-col items-center justify-center">
        <h1 className="text-4xl font-bold text-gray-800 mb-8">Skapa Konto</h1>
        <div className="bg-slate-300 border-2 border-slate-600 rounded-lg p-8 shadow-lg max-w-md w-full mx-4">
          <form>
            <div className="mb-4">
              <div className="bg-slate-200 p-2 rounded-lg mb-2">
                <label className="block text-black">Email</label>
              </div>
              <input type="email" className="w-full p-2 rounded border border-slate-400" />
            </div>
            <div className="mb-4">
              <div className="bg-slate-200 p-2 rounded-lg mb-2">
                <label className="block text-black">Lösenord</label>
              </div>
              <input type="password" className="w-full p-2 rounded border border-slate-400" />
            </div>
            <button type="submit" className="w-full bg-slate-300 text-black hover:text-gray-700 hover:scale-105 border-2 hover:bg-slate-400 border-slate-600 rounded-lg p-1 shadow-lg">
              Skapa Konto
            </button>
          </form>
          
          <div className="mt-8 bg-slate-200 p-4 rounded-lg">
            <h2 className="text-xl font-semibold mb-4">Fördelar med ett konto:</h2>
            <ul className="space-y-3">
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <span>Spara dina PC-byggen och återkom till dem senare</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <span>Få personliga rekommendationer från vår AI för din datorbygge</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateAccount;