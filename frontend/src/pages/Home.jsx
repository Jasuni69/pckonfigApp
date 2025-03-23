import React from "react";
import { Link } from "react-router-dom";

const Home = () => {
  return (
    <div className="wrapper bg-gradient-to-b from-slate-300 to-slate-200">
      <div className="flex justify-center items-center min-h-screen pt-16">
        <div className="container px-4 flex flex-col items-center">
          <h1 className="text-4xl md:text-5xl font-bold text-slate-800 text-center">
            Bygg Din Drömdator
          </h1>
          <p className="text-xl text-slate-700 mt-6 text-center max-w-2xl">
            Skapa din perfekta dator med vår användarvänliga byggverktyg. 
            Jämför komponenter och kontrollera kompatibilitet.
          </p>
          
          <div className="mt-12 flex gap-6 flex-wrap justify-center">
            <Link to="/pcbuilder" className="bg-slate-300 text-black hover:text-gray-700 hover:scale-105 border-2 hover:bg-slate-400 border-slate-600 rounded-lg p-1 shadow-lg">
              Börja Bygga
            </Link>
            <Link to="/savedbuilds" className="bg-slate-300 text-black hover:text-gray-700 hover:scale-105 border-2 hover:bg-slate-400 border-slate-600 rounded-lg p-1 shadow-lg">
              Se Dina Byggen
            </Link>
            <Link to="/createaccount" className="bg-slate-300 text-black hover:text-gray-700 hover:scale-105 border-2 hover:bg-slate-400 border-slate-600 rounded-lg p-1 shadow-lg">
               Skapa Konto
            </Link>
          </div>

          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-4xl">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="font-semibold text-xl mb-2">Kompatibilitetskontroll</h3>
              <p className="text-gray-600">Säkerställ att alla komponenter fungerar perfekt tillsammans.</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="font-semibold text-xl mb-2">Prestandaöversikt</h3>
              <p className="text-gray-600">Få rekommendationer baserade på dina behov.</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="font-semibold text-xl mb-2">Skapa konto</h3>
              <p className="text-gray-600">Skapa konto för att kunna spara dina byggen och få rekommendationer på komponenter.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
