import React from "react";
const Searchbar = () => {
    return (
      <div className="flex rounded-md border-2 border-slate-800 overflow-hidden max-w-md mx-auto">
        <input 
          type="text" 
          placeholder="Search Something..." 
          className="w-full outline-none bg-white text-gray-600 text-sm px-4 py-3"
        />
        <button type="button" className="flex items-center justify-center bg-slate-500 px-5 hover:bg-slate-600">
            <img src="/src/assets/icons/search.svg" alt="search" className=" w-8 h-8"/>
        </button>
      </div>
    )
  }
  
  export default Searchbar