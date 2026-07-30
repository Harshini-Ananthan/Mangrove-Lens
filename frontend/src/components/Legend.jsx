import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiInfo } from 'react-icons/fi';

export const Legend = ({ layers }) => {
  // Only show if relevant layers are active
  const showNdvi = layers.ndvi;
  const showExtent = layers.mangrove_extent;

  if (!showNdvi && !showExtent) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 20 }}
        className="absolute bottom-6 left-6 z-[1000] bg-white/95 backdrop-blur shadow-lg rounded-2xl p-4 border border-white/40 w-56 pointer-events-auto"
      >
        <div className="flex items-center gap-2 mb-3">
          <FiInfo className="text-secondary" />
          <h4 className="text-xs font-bold text-gray-700 uppercase tracking-widest">Map Legend</h4>
        </div>

        <div className="flex flex-col gap-4">
          {showNdvi && (
            <div>
              <div className="flex justify-between text-[10px] text-gray-500 mb-1 font-medium">
                <span>Low Vegetation</span>
                <span>Healthy Mangrove</span>
              </div>
              <div className="h-2.5 w-full rounded-full bg-gradient-to-r from-yellow-100 via-yellow-400 to-green-600 shadow-inner"></div>
              <div className="flex justify-between text-[10px] text-gray-400 mt-1">
                <span>0.0</span>
                <span>1.0</span>
              </div>
            </div>
          )}

          {showExtent && (
            <div className="flex items-center gap-3">
              <div className="w-4 h-4 rounded bg-[#0F766E] border border-white shadow-sm opacity-80"></div>
              <span className="text-xs text-gray-600 font-medium">Mangrove Extent Area</span>
            </div>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
};
