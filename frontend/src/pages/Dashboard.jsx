import React, { useCallback, useEffect, useState } from 'react';
import { FiChevronRight } from 'react-icons/fi';
import { Sidebar } from '../components/Sidebar';
import { MapView } from '../components/MapView';
import { FloatingControls } from '../components/FloatingControls';
import { BottomStatusBar } from '../components/BottomStatusBar';

import { Legend } from '../components/Legend';
import { TopRightLogo } from '../components/TopRightLogo';
import { approveAlert, dispatchAlert, downloadMonitoringReport, fetchAlertOutbox, fetchAoi, fetchLiveMapTiles, fetchMonitoringDecisions, fetchMonitoringFeatures, runMonitoring, waitForMonitoringJob } from '../api';

export const Dashboard = () => {
  // State for Map
  const [center, setCenter] = useState({ lat: 21.9497, lng: 89.1833 });
  const [zoom, setZoom] = useState(9);
  
  // State for live analysis
  const [analysisData, setAnalysisData] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [trendData, setTrendData] = useState([]);
  const [aoi, setAoi] = useState(null);
  const [error, setError] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [liveTile, setLiveTile] = useState(null);
  const [dataRevision, setDataRevision] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  
  // State for Timeline
  const [selectedYear, setSelectedYear] = useState(2025);

  // State for Layers
  const [layers, setLayers] = useState({
    mangrove_extent: true,
    ndvi: false,
    satellite: true,
  });

  const refresh = useCallback(async () => {
    const [features, decisions, operationalAoi, alertRows] = await Promise.all([
      fetchMonitoringFeatures(), fetchMonitoringDecisions(), fetchAoi(), fetchAlertOutbox(),
    ]);
    setAoi(operationalAoi);
    setAlerts(alertRows);
    const ordered = [...features].reverse();
    setTrendData(ordered.map(row => ({ period: row.period_start, ndvi: row.ndvi_mean })));
    const selectedPeriod = `${selectedYear}-06-01`;
    const selectedFeature = features.find(row => row.period_start === selectedPeriod);
    const decision = decisions.find(row => row.period_start === selectedPeriod);
    setDataRevision(selectedFeature?.updated_at || null);
    if (selectedFeature) {
      setAnalysisData({
        ndvi_actual: selectedFeature.ndvi_mean,
        ndvi_predicted: decision?.expected_ndvi ?? null,
        co_level: selectedFeature.co_mean,
        health_score: decision ? 100 - decision.risk_score : null,
        severity: decision?.severity ?? null,
        decision_id: decision?.id ?? null,
      });
    } else setAnalysisData(null);
  }, [selectedYear]);

  useEffect(() => {
    refresh().catch(err => setError(err.response?.data?.detail || err.message));
    const timer = window.setInterval(() => refresh().catch(err => setError(err.response?.data?.detail || err.message)), 15000);
    return () => window.clearInterval(timer);
  }, [refresh]);

  useEffect(() => {
    if (!layers.ndvi) {
      setLiveTile(null);
      return;
    }
    setError(null);
    fetchLiveMapTiles(`${selectedYear}-06-01`)
      .then(setLiveTile)
      .catch(err => {
        setLiveTile(null);
        setError(err.response?.data?.detail || err.message);
      });
  }, [layers.ndvi, selectedYear, dataRevision]);

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

  const handleAnalyze = async () => {
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
        {sidebarOpen ? <Sidebar
          selectedYear={selectedYear}
          setSelectedYear={setSelectedYear}
          layers={layers}
          toggleLayer={toggleLayer}
          analysisData={analysisData}
          isAnalyzing={isAnalyzing}
          trendData={trendData}
          error={error}
          alerts={alerts}
          onApproveAlert={async id => { await approveAlert(id, 'dashboard-operator'); await refresh(); }}
          onDispatchAlert={async id => { await dispatchAlert(id); await refresh(); }}
          onClose={() => setSidebarOpen(false)}
          canExport={Boolean(analysisData?.decision_id)}
          onExportReport={() => downloadMonitoringReport(analysisData.decision_id).catch(err => setError(err.response?.data?.detail || err.message))}
        /> : (
          <button onClick={() => setSidebarOpen(true)} aria-label="Open sidebar" className="absolute left-4 top-4 z-[1100] rounded-xl bg-primary p-3 text-white shadow-lg hover:bg-secondary">
            <FiChevronRight size={20} />
          </button>
        )}
        
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
            aoiGeoJSON={aoi}
            liveTile={liveTile}
          />

          <Legend layers={layers} />

          <FloatingControls 
            onReset={handleReset}
            onLocate={handleLocate}
            onFullscreen={handleFullscreen}
            isAnalyzing={isAnalyzing}
            canAnalyze={selectedYear >= 2020}
            onAnalyze={handleAnalyze}
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
