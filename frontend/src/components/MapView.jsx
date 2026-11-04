import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMapEvents } from 'react-leaflet';
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

export const MapView = ({ center, zoom, layers, setCenter, setZoom, aoiGeoJSON, liveTile }) => {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    return (
      <div className="w-full h-full bg-gray-100 animate-pulse flex items-center justify-center">
        <span className="text-gray-400 font-medium">Initializing Map Engine...</span>
      </div>
    );
  }

  // The GeoJSON is the operational monitoring boundary, not a vegetation raster.
  const geoJsonStyle = {
    fillColor: '#0F766E',
    weight: 2,
    opacity: 1,
    color: 'white',
    fillOpacity: 0.08
  };

  return (
    <div className="w-full h-full relative z-0">
      
      <MapContainer 
        center={center} 
        zoom={zoom} 
        zoomControl={false}
        className="w-full h-full cursor-crosshair"
      >
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

        {layers.ndvi && liveTile?.tile_url && (
          <TileLayer
            key={`${liveTile.period_start}-${liveTile.query_executed_at}`}
            url={liveTile.tile_url}
            opacity={0.72}
            attribution={`Google Earth Engine · ${liveTile.source_collection}`}
          />
        )}

        {layers.mangrove_extent && aoiGeoJSON && (
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
