import React from 'react';
import { FiMapPin } from 'react-icons/fi';

export const SearchBox = () => {
  return (
    <div className="flex items-center bg-gray-50 rounded-xl px-3 py-3 border border-gray-100 shadow-sm focus-within:border-secondary focus-within:ring-1 focus-within:ring-secondary transition-all">
      <FiMapPin className="text-secondary mr-2" />
      <input 
        type="text" 
        placeholder="Search specific location..." 
        className="bg-transparent border-none outline-none w-full text-sm text-gray-700 placeholder-gray-400"
      />
    </div>
  );
};
