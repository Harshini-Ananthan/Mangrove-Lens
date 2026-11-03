import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMapEvents, Polygon } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

// Component to handle map events and report back to parent
const MapEvents = ({ onMove, onZoom }) => {
  useMapEvents({
    moveend: (e) => {
      onMove(e.target.getCenter());
    },
    zoomend: (e) => {
      onZoom(e.target.getZoom());
    },
  });
  return null;
};

// Custom Polygon Drawer
const PolygonDrawer = ({ isDrawing, onPolygonComplete }) => {
  const [points, setPoints] = useState([]);

  useMapEvents({
    click(e) {
      if (!isDrawing) return;
      const newPoints = [...points, [e.latlng.lat, e.latlng.lng]];
      setPoints(newPoints);
      
      // Auto-complete if they have at least 3 points and double click or something.
      // We will just let them click a 'Finish' button outside instead.
    },
    contextmenu() {
      if (!isDrawing) return;
      // Right click to finish
      if (points.length >= 3) {
        onPolygonComplete(points);
        setPoints([]);
      }
    }
  });

  if (!isDrawing || points.length === 0) return null;
  return <Polygon positions={points} pathOptions={{ color: 'blue' }} />;
};

export const MapView = ({ center, zoom, layers, setCenter, setZoom, onPolygonDrawn, isDrawingMode, setIsDrawingMode, aoiGeoJSON }) => {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  const handlePolygonComplete = (points) => {
    setIsDrawingMode(false);
    
    // Convert Leaflet points [lat, lng] to GeoJSON geometry
    const coordinates = [...points, points[0]].map(p => [p[1], p[0]]); // [lng, lat]
    const geoJson = {
      type: "Feature",
      geometry: {
        type: "Polygon",
        coordinates: [coordinates]
      },
      properties: {}
    };
    
    if (onPolygonDrawn) {
      onPolygonDrawn(geoJson);
    }
  };

  if (!isMounted) {
    return (
      <div className="w-full h-full bg-gray-100 animate-pulse flex items-center justify-center">
        <span className="text-gray-400 font-medium">Initializing Map Engine...</span>
      </div>
    );
  }

  // Define GeoJSON style based on active layers
  const geoJsonStyle = {
    fillColor: layers.ndvi ? '#22C55E' : '#0F766E',
    weight: 2,
    opacity: 1,
    color: 'white',
    fillOpacity: 0.4
  };

  return (
    <div className="w-full h-full relative z-0">
      
      {isDrawingMode && (
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-[1000] bg-white px-4 py-2 rounded-lg shadow-lg border-2 border-primary text-sm font-medium animate-pulse">
          Click on map to draw points. Right-click to finish.
        </div>
      )}

      <MapContainer 
        center={center} 
        zoom={zoom} 
        zoomControl={false}
        className="w-full h-full cursor-crosshair"
      >
        <PolygonDrawer isDrawing={isDrawingMode} onPolygonComplete={handlePolygonComplete} />

        {/* Base Layer */}
        {layers.satellite ? (
          <TileLayer
            url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            attribution='&copy; <a href="https://www.esri.com/">Esri</a>'
          />
        ) : (
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          />
        )}

        {/* Mangrove Extent / NDVI Layer (Mocked with GeoJSON) */}
        {(layers.mangrove_extent || layers.ndvi) && aoiGeoJSON && (
          <GeoJSON 
            key={`sundarbans-${layers.ndvi ? 'ndvi' : 'extent'}`} 
            data={aoiGeoJSON}
            style={geoJsonStyle} 
          />
        )}

        <MapEvents onMove={setCenter} onZoom={setZoom} />
      </MapContainer>
    </div>
  );
};
