# Urban Accessibility Analysis

## Purpose

This project analyzes urban accessibility metrics across multiple cities to evaluate how accessible different areas are based on proximity to essential services and transportation infrastructure. The analysis combines geospatial data processing with interactive visualization to provide insights into urban accessibility patterns.

## Scope

Currently includes accessibility analysis for the following cities:
- Adelaide, South Australia, Australia
- Berlin, Germany
- Hobart, Tasmania, Australia
- Paris, Île-de-France, France
- Toronto, Ontario, Canada

The project processes geospatial data to generate accessibility metrics and visualizes the results through an interactive web interface.

## Tech Stack

### Frontend
- **Angular** - Web framework for interactive visualization
- **TypeScript** - Programming language
- **SCSS** - Styling

### Backend / Analysis
- **Python** - Data processing and analysis
- **Jupyter Notebooks** - Interactive analysis and documentation
- **GeoPandas** - Geospatial data analysis
- **GeoJSON** - Vector geospatial data format
- **GeoPackage (.gpkg)** - Spatial database format

### Data
- GeoJSON files for city-level accessibility analysis
- GeoPackage databases for efficient spatial queries

## Project Structure

```
urban-accessibility-analysis/
├── frontend/              # Angular web application
│   ├── src/             # Angular source code
│   └── public/          # Static assets including geojson data
├── notebooks/           # Jupyter notebooks for analysis pipeline
├── gis-env/            # Python virtual environment for GIS tools
└── README.md           # This file
```

## Getting Started

### Prerequisites
- Node.js and npm (for frontend development)
- Python 3.x (for geospatial analysis)

### Installation

**Frontend:**
```bash
cd frontend
npm install
```

**Backend/Analysis:**
```bash
# Activate the GIS environment
source gis-env/Scripts/activate  # On Windows: gis-env\Scripts\Activate.ps1

# Install dependencies if needed
pip install -r requirements.txt
```

### Running the Project

**Frontend Development:**
```bash
cd frontend
ng serve
```

**Jupyter Notebooks:**
```bash
jupyter notebook notebooks/
```

## Future Plans

- [ ] Add more cities to the analysis
- [ ] Implement additional accessibility metrics
- [ ] Add data export and reporting features
- [ ] Enhance visualization capabilities
- [ ] Create automated data update pipeline
- [ ] Add user documentation and tutorials

