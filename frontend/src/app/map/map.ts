import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LeafletModule } from '@asymmetrik/ngx-leaflet';
import {
  tileLayer,
  MapOptions,
  GeoJSONOptions,
  geoJSON as leafletGeoJSON,
  GeoJSON,
  Map as LeafletMap,
  Layer
} from 'leaflet';
import { CategorySelectorComponent } from '../category-selector/category-selector';
import { CitySelectorComponent } from '../city-selector/city-selector';
import { ThresholdSelectorComponent } from '../threshold-selector/threshold-selector';
import { CATEGORY_OPTIONS } from '../category-selector/category-selector.constants';
import {
  DEFAULT_MAP_OPTIONS,
  DEFAULT_SELECTED_CATEGORIES,
  DEFAULT_SELECTED_CITY,
  DEFAULT_SELECTED_THRESHOLD,
  MAP_BASE_LAYER_NAME,
  MAP_OVERLAY_NAME,
  MAP_TILE_OPTIONS,
  MAP_TILE_URL,
  FULL_MATCH_STYLE,
  ALMOST_MATCH_STYLE,
  NO_MATCH_STYLE,
  CITY_GEOJSON_FILES
} from './map.constants';
import {
  buildFeaturePopupLabel,
  getGeoJsonUrl,
  getMatchCount
} from '../utils/component-utils';

@Component({
  selector: 'app-map',
  standalone: true,
  imports: [CommonModule, LeafletModule, CategorySelectorComponent, CitySelectorComponent, ThresholdSelectorComponent],
  templateUrl: './map.html',
  styleUrls: ['./map.scss']
})
export class MapComponent {
  protected options: MapOptions = DEFAULT_MAP_OPTIONS;

  protected selectedCategories: string[] = DEFAULT_SELECTED_CATEGORIES;
  protected selectedThreshold = DEFAULT_SELECTED_THRESHOLD;
  protected selectedCity: string = DEFAULT_SELECTED_CITY;
  protected readonly densityThresholdNote = 'This map shows urban extents identified by a preprocessing filter: only census areas with > 1000 people/km² density are included, then clustered and filtered to cities with population ≥ 100k and area ≥ 50 km².';

  private readonly categoryLabelByValue: Record<string, string> = CATEGORY_OPTIONS.reduce(
    (acc, option) => ({ ...acc, [option.value]: option.label }),
    {} as Record<string, string>
  );

  private baseLayer = tileLayer(MAP_TILE_URL, MAP_TILE_OPTIONS);

  protected layers: Layer[] = [this.baseLayer];

  protected layersControl: {
    baseLayers: Record<string, Layer>;
    overlays: Record<string, Layer>;
  } = {
    baseLayers: {
      [MAP_BASE_LAYER_NAME]: this.baseLayer
    },
    overlays: {}
  };

  private cityGeoJsonFiles: Record<string, string> = CITY_GEOJSON_FILES;
  private readonly fitPadding: [number, number] = [20, 20];
  private readonly initialZoomInFromFit = 0.5;

  protected geoJsonOptions: GeoJSONOptions = {
    style: (feature) => this.getFeatureStyle(feature),
    onEachFeature: (feature, layer) => {
      if (feature.properties) {
        const props = feature.properties as Record<string, any>;
        const label = buildFeaturePopupLabel(props);
        layer.bindPopup(label || 'Accessibility feature');
      }
    }
  };

  protected get selectedCategoryLabels(): string[] {
    return this.selectedCategories.map(
      (value) => this.categoryLabelByValue[value] ?? value
    );
  }

  private getFeatureStyle(feature: any) {
    const props = feature?.properties as Record<string, any> | undefined;

    if (!props || this.selectedCategories.length === 0) {
      return {
        stroke: false,
        fill: false,
        fillOpacity: 0,
        opacity: 0
      };
    }

    const matchCount = getMatchCount(props, this.selectedCategories, this.selectedThreshold);

    if (matchCount === this.selectedCategories.length) {
      return FULL_MATCH_STYLE;
    }

    if (this.selectedCategories.length > 1 && matchCount === this.selectedCategories.length - 1) {
      return ALMOST_MATCH_STYLE;
    }

    return NO_MATCH_STYLE;
  }

  private geoJsonLayer?: GeoJSON;
  private map?: LeafletMap;

  protected onMapReady(map: LeafletMap): void {
    this.map = map;
    this.loadCityLayer(this.selectedCity);
  }

  protected onCategoriesSelected(categories: string[]): void {
    this.selectedCategories = categories;
    this.geoJsonLayer?.setStyle(this.geoJsonOptions.style as any);
  }

  protected onThresholdSelected(threshold: number): void {
    this.selectedThreshold = threshold;
    this.geoJsonLayer?.setStyle(this.geoJsonOptions.style as any);
  }

  protected onCitySelected(city: string): void {
    if (!city || city === this.selectedCity) {
      return;
    }

    this.selectedCity = city;
    this.loadCityLayer(city);
  }

  private loadCityLayer(city: string): void {
    const url = getGeoJsonUrl(city, this.cityGeoJsonFiles);

    if (!url) {
      console.error(`No GeoJSON file configured for city: ${city}`);
      return;
    }

    fetch(url)
      .then((response) => response.json())
      .then((data) => {
        this.removeCurrentCityLayer();

        this.geoJsonLayer = leafletGeoJSON(data, this.geoJsonOptions);
        this.layers = [this.baseLayer, this.geoJsonLayer];
        this.layersControl = {
          baseLayers: this.layersControl.baseLayers,
          overlays: {
            [MAP_OVERLAY_NAME]: this.geoJsonLayer
          }
        };

        if (this.map) {
          this.geoJsonLayer.addTo(this.map);
          const bounds = this.geoJsonLayer.getBounds();
          if (bounds.isValid()) {
            this.map.fitBounds(bounds, { padding: this.fitPadding });
            const currentZoom = this.map.getZoom();
            const maxZoom = this.map.getMaxZoom();
            const targetZoom = Math.min(currentZoom + this.initialZoomInFromFit, maxZoom);
            this.map.setZoom(targetZoom);
          }
        }
      })
      .catch((error) => {
        console.error(`Failed to load GeoJSON for ${city}:`, error);
      });
  }

  private removeCurrentCityLayer(): void {
    if (this.geoJsonLayer && this.map) {
      this.map.removeLayer(this.geoJsonLayer);
    }

    this.geoJsonLayer = undefined;
    this.layers = [this.baseLayer];
    this.layersControl = {
      baseLayers: this.layersControl.baseLayers,
      overlays: {}
    };
  }
}
