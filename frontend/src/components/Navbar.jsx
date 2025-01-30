import React from "react";
import { Link } from "react-router-dom";
import Searchbar from "./Searchbar";

const Navbar = () => {
  return (
    <nav className="h-auto min-w-full max-w-full fixed top-0 bg-slate-100 z-50">

        <div className="flex h-16 items-center">
          <div className="pl-2 flex flex-1">
              <Link to="/" className="flex gap-4 items-center">
                <img src="/src/assets/logos/pc.svg" alt="" className="h-8 w-8"/>
                <span className="text-lg text-black font-bold">PCkonfig.se</span>
              </Link>
          </div>
          <div className="flex pr-8 gap-4 items-center">
              <Searchbar />
              <Link to="/about" className="text-gray-600 hover:text-gray-900">Placeholder2</Link>
              <Link to="/contact" className="text-gray-600 hover:text-gray-900">Placeholder3</Link>
          </div>
        </div>

        <div className="flex bg-slate-500 h-12 px-4 items-center gap-4 pl-14">
            <Link to="/pcbuilder" className="bg-slate-300 text-black hover:text-gray-700 hover:scale-105 border-2 hover:bg-slate-400 border-slate-600 rounded-lg p-1 shadow-lg">Bygg din PC</Link>
            <Link to="/pcparts" className="bg-slate-300 text-black hover:text-gray-700 hover:scale-105 border-2 hover:bg-slate-400 border-slate-600 rounded-lg p-1 shadow-lg">PC-delar</Link>
            <Link to="/savedbuilds" className="bg-slate-300 text-black hover:text-gray-700 hover:scale-105 border-2 hover:bg-slate-400 border-slate-600 rounded-lg p-1 shadow-lg">Sparade byggen</Link>
        </div>  

    </nav>
  );
};

export default Navbar;
