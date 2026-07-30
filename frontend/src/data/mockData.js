export const statsData = {
  mangroveArea: "147,283 km²",
  ndvi: "0.73",
  carbonEmissions: "13.2 MT",
  predictionScore: "92%"
};

export const layerOptions = [
  { id: "mangrove_extent", label: "Mangrove Extent", defaultActive: true },
  { id: "ndvi", label: "NDVI", defaultActive: false },
  { id: "carbon", label: "Carbon Emission", defaultActive: false },
  { id: "prediction", label: "AI Prediction", defaultActive: false },
  { id: "stations", label: "Monitoring Stations", defaultActive: true },
  { id: "satellite", label: "Satellite Base", defaultActive: true }
];

export const timelineYears = [1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2025];

export const trendData = [
  { year: 1985, area: 155000, ndvi: 0.76 },
  { year: 1990, area: 152000, ndvi: 0.75 },
  { year: 1995, area: 150500, ndvi: 0.74 },
  { year: 2000, area: 149000, ndvi: 0.73 },
  { year: 2005, area: 148200, ndvi: 0.72 },
  { year: 2010, area: 147800, ndvi: 0.73 },
  { year: 2015, area: 147500, ndvi: 0.74 },
  { year: 2020, area: 147400, ndvi: 0.73 },
  { year: 2025, area: 147283, ndvi: 0.73 },
];

export const mockStations = [
  { id: 1, name: "Sunderbans Alpha", lat: 21.9497, lng: 89.1833, status: "Active", sensor: "Multispectral" },
  { id: 2, name: "Bidyadhari Post", lat: 22.1245, lng: 88.8500, status: "Active", sensor: "LiDAR" },
  { id: 3, name: "Hiron Point", lat: 21.7833, lng: 89.4667, status: "Maintenance", sensor: "Soil Carbon" },
];

export const sundarbansGeoJSON = {
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": { "name": "Sundarbans Protected Area" },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [88.8, 22.2],
            [89.5, 22.2],
            [89.5, 21.6],
            [88.8, 21.6],
            [88.8, 22.2]
          ]
        ]
      }
    }
  ]
};
