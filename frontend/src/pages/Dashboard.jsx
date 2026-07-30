import React, { useState } from 'react';
import { Navbar } from '../components/Navbar';
import { Sidebar } from '../components/Sidebar';
import { MapView } from '../components/MapView';
import { FloatingControls } from '../components/FloatingControls';
import { BottomStatusBar } from '../components/BottomStatusBar';

import { Legend } from '../components/Legend';
import { TopRightLogo } from '../components/TopRightLogo';
import { runAnalysis } from '../api';

export const Dashboard = () => {
  // State for Map
  const [center, setCenter] = useState({ lat: 21.9497, lng: 89.1833 });
  const [zoom, setZoom] = useState(9);
  
  // State for live analysis
  const [analysisData, setAnalysisData] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isDrawingMode, setIsDrawingMode] = useState(false);
  
  // State for Timeline
  const [selectedYear, setSelectedYear] = useState(2025);

  // State for Layers
  const [layers, setLayers] = useState({
    mangrove_extent: true,
    ndvi: false,
    carbon: false,
    prediction: false,
    stations: true,
    satellite: true,
  });

  const toggleLayer = (layerId) => {
    setLayers(prev => ({
      ...prev,
      [layerId]: !prev[layerId]
    }));
  };

  const handleReset = () => {
    setCenter({ lat: 21.9497, lng: 89.1833 });
    setZoom(9);
  };

  const handleLocate = () => {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition((position) => {
        setCenter({
          lat: position.coords.latitude,
          lng: position.coords.longitude
        });
        setZoom(12);
      });
    }
  };

  const handlePolygonDrawn = async (geoJsonData) => {
    try {
      setIsAnalyzing(true);
      // Run the full Phase 2 Pipeline
      const result = await runAnalysis("custom_region", geoJsonData, `${selectedYear}-06-01T00:00:00Z`);
      setAnalysisData(result.results);
      console.log("Analysis Result:", result);
      
      // If there's an alert triggered, we could show a toast or a modal here
      if (result.results.alert_triggered) {
        alert(`🚨 ALERT TRIGGERED: Mangrove Health is ${result.results.health_status}. Please check the alerts panel for details.`);
      }
    } catch (error) {
      console.error("Failed to run analysis:", error);
      alert("Failed to run analysis. Check console for details.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(err => {
        console.error(`Error attempting to enable fullscreen mode: ${err.message}`);
      });
    } else {
      document.exitFullscreen();
    }
  };

  const activeLayersCount = Object.values(layers).filter(Boolean).length;

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden bg-background">
      
      <div className="flex-1 flex overflow-hidden relative">
        {/* Sidebar */}
        <Sidebar 
          selectedYear={selectedYear}
          setSelectedYear={setSelectedYear}
          layers={layers}
          toggleLayer={toggleLayer}
          analysisData={analysisData}
          isAnalyzing={isAnalyzing}
        />
        
        {/* Main Map Area */}
        <main className="flex-1 relative">
          <TopRightLogo />

          <MapView 
            center={center}
            zoom={zoom}
            setCenter={setCenter}
            setZoom={setZoom}
            selectedYear={selectedYear}
            layers={layers}
            onPolygonDrawn={handlePolygonDrawn}
            isDrawingMode={isDrawingMode}
            setIsDrawingMode={setIsDrawingMode}
          />

          <Legend layers={layers} />

          <FloatingControls 
            onReset={handleReset}
            onLocate={handleLocate}
            onFullscreen={handleFullscreen}
            isDrawingMode={isDrawingMode}
            onDrawToggle={() => setIsDrawingMode(!isDrawingMode)}
          />

          <BottomStatusBar 
            zoom={zoom}
            year={selectedYear}
            coordinates={center}
            activeLayersCount={activeLayersCount}
          />
        </main>
      </div>
    </div>
  );
};
