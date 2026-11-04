export const layerOptions = [
  { id: "mangrove_extent", label: "Operational AOI", defaultActive: true },
  { id: "ndvi", label: "Live Earth Engine NDVI", defaultActive: false },
  { id: "satellite", label: "Satellite Base", defaultActive: true },
];

export const timelineYears = Array.from(
  { length: new Date().getFullYear() - 2019 + 1 },
  (_, index) => 2019 + index,
);
