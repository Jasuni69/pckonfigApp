import React from "react";
import { Link } from "react-router-dom";

const Footer = () => {
  return (
    <footer className="flex h-42 min-w-full justify-evenly items-center bg-slate-100">
      <div className="flex flex-col gap-4 pl-16">
        <a href="#" className="text-gray-600 hover:text-gray-900">Placeholder1</a>
        <a href="#" className="text-gray-600 hover:text-gray-900">Placeholder2</a>
        <a href="#" className="text-gray-600 hover:text-gray-900">Placeholder3</a>
      </div>
      <div className="flex flex-col gap-4">
        <a href="#" className="text-gray-600 hover:text-gray-900">Placeholder1</a>
        <a href="#" className="text-gray-600 hover:text-gray-900">Placeholder2</a>
        <a href="#" className="text-gray-600 hover:text-gray-900">Placeholder3</a>
      </div>
      <div className="flex flex-col gap-4 pr-16">
        <Link to="/" className="text-gray-600 hover:text-gray-900">Home</Link>
        <Link to="/about" className="text-gray-600 hover:text-gray-900">About</Link>
        <Link to="/contact" className="text-gray-600 hover:text-gray-900">Contact</Link>
      </div>
    </footer>
  );
};

export default Footer;
