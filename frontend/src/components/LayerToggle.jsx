import React from 'react';
import { motion } from 'framer-motion';

export const LayerToggle = ({ id, label, active, onToggle }) => {
  return (
    <div className="flex items-center justify-between py-2">
      <span className="text-sm font-medium text-gray-700">{label}</span>
      <button
        onClick={() => onToggle(id)}
        className={`w-11 h-6 rounded-full p-1 transition-colors duration-300 ease-in-out focus:outline-none ${
          active ? 'bg-secondary' : 'bg-gray-200'
        }`}
      >
        <motion.div
          layout
          initial={false}
          animate={{ x: active ? 20 : 0 }}
          className="w-4 h-4 bg-white rounded-full shadow-sm"
        />
      </button>
    </div>
  );
};
