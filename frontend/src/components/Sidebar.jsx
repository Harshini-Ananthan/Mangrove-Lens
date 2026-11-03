import React from 'react';
import { motion } from 'framer-motion';
import { FiDownload, FiMenu, FiGlobe, FiHelpCircle, FiFileText } from 'react-icons/fi';
import { SearchBox } from './SearchBox';
import { StatsCard } from './StatsCard';
import { TimelineSlider } from './TimelineSlider';
import { LayerPanel } from './LayerPanel';
import { PredictionCard } from './PredictionCard';
import { TrendChart } from './TrendChart';
import { statsData } from '../data/mockData';

export const Sidebar = ({ 
  selectedYear, 
  setSelectedYear,
  layers,
  toggleLayer,
  analysisData,
  isAnalyzing,
  trendData,
  systemStatus,
  error
}) => {
  return (
    <motion.aside 
      initial={{ x: -300, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="w-full md:w-[380px] bg-white h-full overflow-y-auto flex flex-col border-r border-gray-100 shadow-[2px_0_15px_rgba(0,0,0,0.03)] z-40 relative"
    >
      {/* Top Left Wavy Header (Replacing Navbar) */}
      <div className="relative w-full overflow-hidden shrink-0 bg-white">
        {/* Wavy SVG Background */}
        <svg viewBox="0 0 320 200" preserveAspectRatio="none" className="absolute top-0 left-0 w-[120%] h-full z-0 drop-shadow-sm">
          <path d="M 0 0 L 320 0 L 320 120 C 250 120 180 200 80 180 C 40 172 20 150 0 140 Z" fill="#C4E4E1" />
          <path d="M 0 0 L 320 0 L 320 100 C 240 100 170 180 80 160 C 40 150 20 135 0 125 Z" fill="#0F766E" />
        </svg>

        <div className="relative z-10 px-4 pt-4 pb-12 flex flex-col">
          {/* Top Nav Links */}
          <div className="flex items-center justify-between text-white text-[10px] font-medium tracking-wide mb-6 opacity-90">
            <button className="flex items-center gap-1.5 hover:opacity-80 transition-opacity"><FiMenu size={14}/> Menu</button>
            <button className="flex items-center gap-1.5 hover:opacity-80 transition-opacity"><FiFileText size={12}/> News</button>
            <button className="flex items-center gap-1.5 hover:opacity-80 transition-opacity"><FiGlobe size={12}/> EN</button>
            <button className="flex items-center gap-1.5 hover:opacity-80 transition-opacity"><FiHelpCircle size={12}/> Help</button>
          </div>
          
          {/* Main Title */}
          <div className="text-center">
            <h2 className="text-3xl font-light text-white tracking-wide">Sundarbans</h2>
          </div>
        </div>
      </div>

      <div className="px-5 pb-5 pt-2 flex-1 flex flex-col gap-5">
        {error && <div role="alert" className="rounded-xl border border-red-200 bg-red-50 p-3 text-xs text-red-700">{error}</div>}
        {systemStatus && (
          <div className="rounded-xl border border-gray-100 bg-gray-50 p-3 text-[11px] text-gray-600">
            <strong className="text-primary">{systemStatus.satellite.provider}</strong> · {systemStatus.satellite.detail}
            {!systemStatus.model.ready && <div className="mt-1 text-amber-700">Using the declared seasonal baseline until a trained model is installed.</div>}
          </div>
        )}
        {/* Search */}
        <SearchBox />

        {/* Timeline */}
        <div className="bg-gray-50/50 rounded-2xl p-4 border border-gray-100 shadow-sm">
          <TimelineSlider selectedYear={selectedYear} onChange={setSelectedYear} />
        </div>

        {/* Statistics Grid */}
        <div className="grid grid-cols-2 gap-2.5 relative">
          {isAnalyzing && (
            <div className="absolute inset-0 bg-white/70 backdrop-blur-sm z-10 flex flex-col items-center justify-center rounded-xl">
              <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin mb-2"></div>
              <span className="text-xs text-primary font-medium">Analyzing Region...</span>
            </div>
          )}
          <StatsCard title="Actual NDVI" value={analysisData ? analysisData.ndvi_actual.toFixed(3) : statsData.ndvi} />
          <StatsCard title="Predicted NDVI" value={analysisData ? analysisData.ndvi_predicted.toFixed(3) : "0.74"} />
          <StatsCard title="Carbon (CO)" value={analysisData ? analysisData.co_level.toFixed(4) : statsData.carbonEmissions} />
          <StatsCard title="Health Score" value={analysisData ? `${analysisData.health_score.toFixed(0)}/100` : statsData.predictionScore} />
        </div>

        {/* Trend Chart */}
        <TrendChart data={trendData} />

        {/* Layer Controls Accordion */}
        <LayerPanel layers={layers} toggleLayer={toggleLayer} />

        {/* AI Prediction */}
        <PredictionCard score={statsData.predictionScore} />
      </div>

      {/* Footer / Download Button */}
      <div className="p-5 border-t border-gray-100 bg-white/80 backdrop-blur-md sticky bottom-0 z-50">
        <button className="w-full py-2.5 bg-gradient-to-r from-primary to-secondary text-white rounded-[14px] text-sm font-semibold shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 hover:-translate-y-0.5">
          <FiDownload />
          <span>Export Report</span>
        </button>
      </div>
    </motion.aside>
  );
};
