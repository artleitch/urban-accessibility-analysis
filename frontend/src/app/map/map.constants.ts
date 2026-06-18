import { LatLngExpression, canvas } from 'leaflet';

export const DEFAULT_MAP_OPTIONS = {
  zoom: 12,
  center: [-34.9285, 138.6007] as LatLngExpression,
  renderer: canvas()
};

export const DEFAULT_SELECTED_CATEGORIES = [
  'education_walk_min',
  'parks_walk_min',
  'transit_walk_min',
  'grocery_walk_min',
  'healthcare_walk_min',
  'libraries_walk_min'
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
  weight: 0.5,
  opacity: 0.8,
  fillColor: '#238b45',
  fillOpacity: 0.7,
  lineJoin: 'round' as const
};

export const ALMOST_MATCH_STYLE = {
  stroke: true,
  fill: true,
  color: '#238b45',
  weight: 0.5,
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
  // Australia
  adelaide: '/adelaide_accessibility.geojson',
  brisbane: '/brisbane_accessibility.geojson',
  canberra: '/canberra_accessibility.geojson',
  melbourne: '/melbourne_accessibility.geojson',
  perth: '/perth_accessibility.geojson',
  sydney: '/sydney_accessibility.geojson',
  // Canada
  toronto: '/toronto_accessibility.geojson',
  victoria: '/victoria_accessibility.geojson',
  edmonton: '/edmonton_accessibility.geojson',
  regina: '/regina_accessibility.geojson',
  winnipeg: '/winnipeg_accessibility.geojson',
  quebec_city: '/quebec_city_accessibility.geojson',
  // Germany
  stuttgart: '/stuttgart_accessibility.geojson',
  munich: '/munich_accessibility.geojson',
  berlin_de: '/berlin_de_accessibility.geojson',
  potsdam: '/potsdam_accessibility.geojson',
  bremen: '/bremen_accessibility.geojson',
  hamburg: '/hamburg_accessibility.geojson',
  wiesbaden: '/wiesbaden_accessibility.geojson',
  schwerin: '/schwerin_accessibility.geojson',
  hanover: '/hanover_accessibility.geojson',
  dusseldorf: '/dusseldorf_accessibility.geojson',
  mainz: '/mainz_accessibility.geojson',
  saarbrucken: '/saarbrucken_accessibility.geojson',
  dresden: '/dresden_accessibility.geojson',
  kiel: '/kiel_accessibility.geojson',
  erfurt: '/erfurt_accessibility.geojson',

  // Other
  berlin: '/berlin_accessibility.geojson',
  paris: '/paris_accessibility.geojson'
};
