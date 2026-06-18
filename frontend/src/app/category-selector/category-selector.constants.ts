export interface CategoryOption {
  label: string;
  value: string;
}

export const CATEGORY_OPTIONS: CategoryOption[] = [
  { label: 'Education', value: 'education_walk_min' },
  { label: 'Parks', value: 'parks_walk_min' },
  { label: 'Transit', value: 'transit_walk_min' },
  { label: 'Groceries', value: 'grocery_walk_min' },
  { label: 'Health Care', value: 'healthcare_walk_min' },
  { label: "Libraries", value: 'libraries_walk_min'}
];
