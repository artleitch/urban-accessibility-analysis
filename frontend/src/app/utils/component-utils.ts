export function isCategorySelected(selectedValues: string[], value: string): boolean {
  return selectedValues.includes(value);
}

export function toggleSelection(selectedValues: string[], value: string, checked: boolean): string[] {
  return checked
    ? [...selectedValues, value]
    : selectedValues.filter((item) => item !== value);
}

export function parseThresholdValue(value: string): number {
  return Number(value);
}

export function buildFeaturePopupLabel(props: Record<string, any>): string {
  return Object.keys(props)
    .filter((key) => key !== 'geometry')
    .map((key) => `${key}: ${props[key]}`)
    .join('<br/>');
}

export function getGeoJsonUrl(city: string, cityMap: Record<string, string>): string | undefined {
  return cityMap[city];
}

export function getMatchCount(
  props: Record<string, any> | undefined,
  selectedCategories: string[],
  threshold: number
): number {
  if (!props) {
    return 0;
  }

  return selectedCategories.reduce((count, category) => {
    const value = props[category];
    return count + (typeof value === 'number' && value <= threshold ? 1 : 0);
  }, 0);
}
