import React from 'react';

export const BottomStatusBar = ({ zoom, year, coordinates, activeLayersCount }) => {
  return (
    <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 z-[1000]">
      <div className="bg-white/90 backdrop-blur-md border border-white/40 shadow-lg rounded-full px-6 py-2.5 flex items-center gap-6 text-[11px] font-medium text-gray-600 uppercase tracking-wide">
        <div className="flex items-center gap-2">
          <span className="opacity-70">Zoom</span>
          <span className="text-primary font-bold">{Math.round(zoom)}</span>
        </div>
        <div className="w-px h-4 bg-gray-200"></div>
        <div className="flex items-center gap-2">
          <span className="opacity-70">Year</span>
          <span className="text-primary font-bold">{year}</span>
        </div>
        <div className="w-px h-4 bg-gray-200"></div>
        <div className="flex items-center gap-2">
          <span className="opacity-70">Center</span>
          <span className="font-mono text-gray-800 tracking-normal">{coordinates.lat.toFixed(4)}, {coordinates.lng.toFixed(4)}</span>
        </div>
        <div className="w-px h-4 bg-gray-200"></div>
        <div className="flex items-center gap-2">
          <span className="opacity-70">Proj</span>
          <span className="font-mono text-gray-800 tracking-normal">EPSG:4326</span>
        </div>
        <div className="w-px h-4 bg-gray-200"></div>
        <div className="flex items-center gap-2">
          <span className="opacity-70">Layers</span>
          <span className="bg-secondary text-white px-2 py-0.5 rounded-full font-bold">{activeLayersCount}</span>
        </div>
      </div>
    </div>
  );
};
