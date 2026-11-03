import React, { useEffect, useState } from 'react';
import { Sidebar } from '../components/Sidebar';
import { MapView } from '../components/MapView';
import { FloatingControls } from '../components/FloatingControls';
import { BottomStatusBar } from '../components/BottomStatusBar';

import { Legend } from '../components/Legend';
import { TopRightLogo } from '../components/TopRightLogo';
import { approveAlert, dispatchAlert, fetchAlertOutbox, fetchAoi, fetchHealth, fetchMonitoringDecisions, fetchMonitoringFeatures, runMonitoring, waitForMonitoringJob } from '../api';

export const Dashboard = () => {
  // State for Map
  const [center, setCenter] = useState({ lat: 21.9497, lng: 89.1833 });
  const [zoom, setZoom] = useState(9);
  
  // State for live analysis
  const [analysisData, setAnalysisData] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isDrawingMode, setIsDrawingMode] = useState(false);
  const [trendData, setTrendData] = useState([]);
  const [aoi, setAoi] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);
  const [error, setError] = useState(null);
  const [alerts, setAlerts] = useState([]);
  
  // State for Timeline
  const [selectedYear, setSelectedYear] = useState(2025);

  // State for Layers
  const [layers, setLayers] = useState({
    mangrove_extent: true,
    ndvi: false,
    carbon: false,
    prediction: false,
    satellite: true,
  });

  const refresh = async () => {
    const [health, features, decisions, operationalAoi, alertRows] = await Promise.all([
      fetchHealth(), fetchMonitoringFeatures(), fetchMonitoringDecisions(), fetchAoi(), fetchAlertOutbox(),
    ]);
    setSystemStatus(health);
    setAoi(operationalAoi);
    setAlerts(alertRows);
    const ordered = [...features].reverse();
    setTrendData(ordered.map(row => ({ period: row.period_start, ndvi: row.ndvi_mean })));
    if (features.length) {
      const latest = features[0];
      const decision = decisions[0];
      setAnalysisData({
        ndvi_actual: latest.ndvi_mean,
        ndvi_predicted: decision?.expected_ndvi ?? latest.ndvi_mean,
        co_level: latest.co_mean,
        health_score: decision ? 100 - decision.risk_score : 100,
        severity: decision?.severity ?? 'low',
      });
    }
  };

  useEffect(() => {
    refresh().catch(err => setError(err.response?.data?.detail || err.message));
  }, []);

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

  const handlePolygonDrawn = async () => {
    try {
      setIsAnalyzing(true);
      setError(null);
      const queued = await runMonitoring(`${selectedYear}-06-01`);
      await waitForMonitoringJob(queued.job_id);
      await refresh();
    } catch (error) {
      console.error("Failed to run analysis:", error);
      setError(error.response?.data?.detail || error.message);
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
          trendData={trendData}
          systemStatus={systemStatus}
          error={error}
          alerts={alerts}
          onApproveAlert={async id => { await approveAlert(id, 'dashboard-operator'); await refresh(); }}
          onDispatchAlert={async id => { await dispatchAlert(id); await refresh(); }}
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
            aoiGeoJSON={aoi}
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
