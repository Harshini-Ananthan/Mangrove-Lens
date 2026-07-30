import React from 'react';
import { FiSearch, FiBell, FiSettings, FiUser } from 'react-icons/fi';
import { LuTrees } from "react-icons/lu";

export const Navbar = () => {
  return (
    <nav className="h-[70px] bg-white shadow-sm sticky top-0 z-50 flex items-center justify-between px-6">
      {/* Logo Section */}
      <div className="flex items-center gap-3 text-primary">
        <LuTrees className="text-3xl" />
        <h1 className="text-xl font-bold tracking-tight">MangroveWatch <span className="text-accent font-medium">AI</span></h1>
      </div>

      {/* Search Bar */}
      <div className="hidden md:flex items-center bg-background rounded-full px-4 py-2 w-1/3 border border-gray-200 focus-within:border-secondary transition-colors">
        <FiSearch className="text-gray-400 mr-2" />
        <input 
          type="text" 
          placeholder="Search coordinates, regions, or projects..." 
          className="bg-transparent border-none outline-none w-full text-sm text-gray-700"
        />
      </div>

      {/* Right Icons */}
      <div className="flex items-center gap-5 text-gray-500">
        <button className="hover:text-secondary transition-colors relative">
          <FiBell className="text-xl" />
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-[10px] rounded-full h-4 w-4 flex items-center justify-center">3</span>
        </button>
        <button className="hover:text-secondary transition-colors">
          <FiSettings className="text-xl" />
        </button>
        <div className="h-8 w-8 rounded-full bg-secondary text-white flex items-center justify-center cursor-pointer shadow-sm hover:opacity-90 transition-opacity">
          <FiUser />
        </div>
      </div>
    </nav>
  );
};
