import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiChevronDown, FiLayers } from 'react-icons/fi';
import { LayerToggle } from './LayerToggle';
import { layerOptions } from '../data/dashboardConfig';

export const LayerPanel = ({ layers, toggleLayer }) => {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 transition-colors"
      >
        <div className="flex items-center gap-2">
          <FiLayers className="text-secondary" />
          <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wider">Map Layers</h3>
        </div>
        <motion.div
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.3 }}
        >
          <FiChevronDown className="text-gray-500" />
        </motion.div>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="p-4 flex flex-col gap-1 border-t border-gray-100">
              {layerOptions.map((layer) => (
                <LayerToggle 
                  key={layer.id} 
                  id={layer.id} 
                  label={layer.label} 
                  active={layers[layer.id]} 
                  onToggle={toggleLayer} 
                />
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
