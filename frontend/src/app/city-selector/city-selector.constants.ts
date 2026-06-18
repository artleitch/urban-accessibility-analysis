export interface CityOption {
  label: string;
  value: string;
  disabled?: boolean;
}

export interface CityGroup {
  country: string;
  options: CityOption[];
}

export const CITY_GROUPS: CityGroup[] = [
  {
    country: 'Australia',
    options: [
      { label: 'Adelaide', value: 'adelaide' },
      { label: 'Brisbane', value: 'brisbane' },
      { label: 'Canberra', value: 'canberra' },
      { label: 'Melbourne', value: 'melbourne' },
      { label: 'Perth', value: 'perth' },
      { label: 'Sydney', value: 'sydney' }
    ]
  },
  {
    country: 'Canada',
    options: [
      { label: 'Edmonton', value: 'edmonton' },
      { label: 'Quebec City', value: 'quebec_city' },
      { label: 'Regina', value: 'regina' },
      { label: 'Toronto', value: 'toronto' },
      { label: 'Victoria', value: 'victoria' },
      { label: 'Winnipeg', value: 'winnipeg' }
    ]
  },
  {
    country: 'Germany',
    options: [
      { label: 'Stuttgart', value: 'stuttgart' },
      { label: 'Munich', value: 'munich' },
      { label: 'Berlin', value: 'berlin' },
      { label: 'Potsdam', value: 'potsdam' },
      { label: 'Bremen', value: 'bremen' },
      { label: 'Hamburg', value: 'hamburg' },
      { label: 'Wiesbaden', value: 'wiesbaden' },
      { label: 'Schwerin', value: 'schwerin' },
      { label: 'Hanover', value: 'hanover' },
      { label: 'Düsseldorf', value: 'dusseldorf' },
      { label: 'Mainz', value: 'mainz' },
      { label: 'Saarbrücken', value: 'saarbrucken' },
      { label: 'Dresden', value: 'dresden' },
      { label: 'Kiel', value: 'kiel' },
      { label: 'Erfurt', value: 'erfurt' }
    ]
  },
  {
    country: 'Other',
    options: [
      { label: 'Berlin', value: 'berlin' },
      { label: 'Paris', value: 'paris' }
    ]
  }
];
