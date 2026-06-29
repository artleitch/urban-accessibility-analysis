import { LatLngExpression } from 'leaflet';

export const DEFAULT_MAP_OPTIONS = {
  zoom: 12,
  center: [-34.9285, 138.6007] as LatLngExpression
};

export const DEFAULT_SELECTED_CATEGORIES = [
  'education_walk_min',
  'parks_walk_min',
  'transit_walk_min',
  'grocery_walk_min',
  'healthcare_walk_min'
];

export const DEFAULT_SELECTED_THRESHOLD = 15;
export const DEFAULT_SELECTED_CITY = 'adelaide';

export const MAP_TILE_URL = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
export const MAP_TILE_OPTIONS = {
  maxZoom: 19,
  attribution: '© OpenStreetMap contributors'
};

export const MAP_BASE_LAYER_NAME = 'OpenStreetMap';
export const MAP_OVERLAY_NAME = 'Accessibility grid';

export const FULL_MATCH_STYLE = {
  stroke: true,
  fill: true,
  color: '#238b45',
  weight: 0.2,
  opacity: 0.8,
  fillColor: '#238b45',
  fillOpacity: 0.7,
  lineJoin: 'round' as const
};

export const ALMOST_MATCH_STYLE = {
  stroke: true,
  fill: true,
  color: '#238b45',
  weight: 0.2,
  opacity: 0.3,
  fillColor: '#238b45',
  fillOpacity: 0.4,
  lineJoin: 'round' as const
};

export const NO_MATCH_STYLE = {
  stroke: false,
  fill: false,
  fillOpacity: 0,
  opacity: 0
};

export const CITY_GEOJSON_FILES: Record<string, string> = {
  adelaide: '/adelaide_accessibility.geojson',
  toronto: '/toronto_accessibility.geojson',
  brisbane: '/brisbane_accessibility.geojson',
  hobart: '/hobart_accessibility.geojson',
  paris: '/paris_accessibility.geojson',
  berlin: '/berlin_accessibility.geojson'
};
