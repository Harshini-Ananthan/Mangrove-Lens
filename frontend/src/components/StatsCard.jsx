import React from 'react';
import { FiTrendingUp, FiCloud, FiMap, FiActivity } from 'react-icons/fi';

const iconMap = {
  "Mangrove Area": <FiMap className="text-secondary opacity-70" />,
  "NDVI": <FiActivity className="text-accent opacity-70" />,
  "Carbon Emissions": <FiCloud className="text-gray-400 opacity-70" />,
  "Prediction Score": <FiTrendingUp className="text-primary opacity-70" />
};

export const StatsCard = ({ title, value, unit }) => {
  return (
    <div className="bg-gradient-to-br from-white to-gray-50/50 p-4 rounded-[20px] shadow-sm border border-gray-100 flex flex-col justify-center transition-all duration-300 hover:-translate-y-1 hover:shadow-md hover:border-secondary/30 relative overflow-hidden group">
      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-secondary/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
      
      <div className="flex items-center gap-2 mb-2">
        {iconMap[title]}
        <h3 className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">{title}</h3>
      </div>
      
      <div className="flex items-baseline gap-1 mt-1">
        <span className="text-2xl font-black text-gray-800 tracking-tight">{value}</span>
        {unit && <span className="text-xs font-medium text-gray-400">{unit}</span>}
      </div>
    </div>
  );
};
