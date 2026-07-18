# Crown Corridor — Next-Gen Real Estate & Geospatial Portal

Crown Corridor is a next-generation real estate and property discovery portal for **Andhra Pradesh** (26 districts) and **Telangana** (33 districts).

The portal integrates verified listings, interactive geospatial maps, local government guidance value estimations, and historical SRO market registration analytics within a single, unified analytical dashboard.

---

## 📂 Repository Layout

The project is structured cleanly to separate the core dashboard application, raw administrative boundaries datasets, documentation vaults, and auxiliary ingestion scrapers:

```
├── index.html                   # Core dashboard portal layout (HTML5 entrypoint)
├── real_estate_portal.js        # Main JavaScript portal logic, listings, and PMTiles map protocol
├── real_estate_styles.css       # Premium CSS design system (Dark mode & glassmorphism)
│
├── data/                        # Consolidated Geographic datasets
│   ├── andhra_pradesh/          # AP specific regions, geoJSON maps, and coordinate metrics
│   │   ├── regions.json
│   │   ├── villages.json
│   │   ├── districts.geojson
│   │   ├── mandals.geojson
│   │   └── coords.json
│   └── telangana/               # TS specific regions, geoJSON maps, and coordinate metrics
│       ├── regions.json
│       ├── villages.json
│       ├── districts.geojson
│       ├── mandals.geojson
│       └── coords.json
│
├── docs/                        # Project documentation files
├── notes/                       # Institutional knowledge vault (Obsidian compatible)
└── scraper/                     # Ingestion scripts used to parse raw LGD directories
```

---

## ⚡ Core Features

1. **Verified Property Listings**:
   - High-fidelity search and filter gallery for villas, apartments, commercial spaces, plots, and agricultural land.
   - Interactive contact forms enabling direct inquiries to SRO verification agents.
2. **Interactive Map Overview**:
   - Bounding district choropleth showing real-time transaction density heat maps. Hover coordinates display metrics; clicking district outlines updates filters.
3. **Geospatial Boundary Explorer**:
   - Integrated drill-down navigation (State → District → Mandal → Village) that flies the map directly to LGD coordinates.
   - Embeds Leaflet PMTiles protocol and MapLibre GL to render high-resolution vector tile cadastral land parcels and survey numbers (Andhra Pradesh BhuNaksha and Telangana BhuBharati) when zoom level >= 11.
   - Evaluates nearby amenities (hospitals, schools, bank branches) using OpenStreetMap data context.
4. **Stamp Duty Calculator**:
   - Computes registration fees dynamically based on state stamp acts (AP combined levy 7.5%, TS combined levy 6.0%).
5. **Government Guidance Directory**:
   - Official valuation guide price directory estimation.
6. **API Console & Webhook Alerts**:
   - Sandbox console fetching simulated JSON transaction data.
   - Alert forms to register webhook emails/SMS triggers for high-value properties.

---

## 🚀 Running Locally

To run the portal locally and enable AJAX queries (`fetch`) to load local GeoJSON files without browser CORS restrictions, start a local HTTP server:

```bash
# Start python local server in the repository root
python3 -m http.server 8080
```

Now, navigate to:
👉 **[http://localhost:8080/index.html](http://localhost:8080/index.html)**

---

## 📔 Documentation and Standards

- **API References**: Auto-generated modules reference sheets are compiled using JSDoc (JS) and `pdoc` (Python):
  ```bash
  npm run docs
  ```
- **Formatting Guidelines**: Plain JS, CSS, HTML, and Markdown are formatted using `Prettier`. Python backend scraper scripts are formatted using `Black`:
  ```bash
  npm run format
  ```
