import React from 'react';
import { FiLayers, FiCrosshair, FiRefreshCw, FiMaximize, FiEdit2 } from 'react-icons/fi';
import { LuRuler } from 'react-icons/lu';

const ControlButton = ({ icon: Icon, label, onClick }) => (
  <button 
    onClick={onClick}
    className="w-10 h-10 bg-white rounded-lg flex items-center justify-center text-gray-600 hover:text-primary hover:bg-gray-50 shadow-sm border border-gray-100 transition-colors group relative"
    aria-label={label}
  >
    <Icon size={18} />
    {/* Tooltip */}
    <span className="absolute right-full mr-2 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap">
      {label}
    </span>
  </button>
);

export const FloatingControls = ({ onReset, onLocate, onFullscreen, onDrawToggle, isDrawingMode }) => {
  return (
    <div className="absolute right-6 bottom-24 z-[1000] flex flex-col gap-2">
      <ControlButton icon={FiLayers} label="Layers" />
      <div className="w-10 h-px bg-gray-200 my-1"></div>
      <ControlButton icon={FiCrosshair} label="Locate Me" onClick={onLocate} />
      <ControlButton icon={FiRefreshCw} label="Reset View" onClick={onReset} />
      <ControlButton icon={FiMaximize} label="Fullscreen" onClick={onFullscreen} />
      <div className="w-10 h-px bg-gray-200 my-1"></div>
      <button 
        onClick={onDrawToggle}
        className={`w-10 h-10 rounded-lg flex items-center justify-center shadow-sm border transition-colors group relative ${isDrawingMode ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 hover:text-primary hover:bg-gray-50 border-gray-100'}`}
        aria-label="Draw Polygon"
      >
        <FiEdit2 size={18} />
        <span className="absolute right-full mr-2 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap">
          {isDrawingMode ? "Cancel Drawing" : "Draw Polygon"}
        </span>
      </button>
      <ControlButton icon={LuRuler} label="Measure Distance" />
    </div>
  );
};
