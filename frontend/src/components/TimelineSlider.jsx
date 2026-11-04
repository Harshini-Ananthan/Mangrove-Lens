import React from 'react';
import { timelineYears } from '../data/dashboardConfig';

export const TimelineSlider = ({ selectedYear, onChange }) => {
  return (
    <div className="py-2 px-1">
      <div className="flex justify-between items-center mb-4">
        <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Time Series</span>
        <span className="text-sm font-black text-secondary bg-secondary/10 px-2 py-0.5 rounded border border-secondary/20">{selectedYear}</span>
      </div>
      
      <div className="relative pt-2 pb-6">
        <input 
          type="range" 
          min="0" 
          max={timelineYears.length - 1} 
          step="1"
          value={timelineYears.indexOf(selectedYear)} 
          onChange={(e) => onChange(timelineYears[e.target.value])}
          className="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-secondary relative z-10"
        />
        
        {/* Custom ticks */}
        <div className="absolute top-2 w-full flex justify-between pointer-events-none px-[2px]">
          {timelineYears.map((year, i) => (
            <div key={year} className="flex flex-col items-center">
              <div className={`w-2 h-2 rounded-full ${year === selectedYear ? 'bg-secondary scale-125' : 'bg-gray-300'} transition-transform z-0 -mt-[2px]`}></div>
              {/* Only show label for some milestones to avoid crowding */}
              {(i === 0 || i === timelineYears.length - 1 || i === Math.floor(timelineYears.length / 2)) && (
                <span className={`text-[10px] mt-2 font-medium ${year === selectedYear ? 'text-secondary' : 'text-gray-400'}`}>
                  {year}
                </span>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
