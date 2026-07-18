# Contributing to Crown Corridor

Thank you for your interest in improving Crown Corridor! 🇮🇳🏙️

We welcome contributions to enhance the next-generation property discovery portal, verified listings database, interactive Leaflet PMTiles overlays, and developer API consoles.

---

## Getting Started

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/mchittineni/CrownCorridor
   cd CrownCorridor
   ```

2. **Run Local Server**:
   To preview the app locally and prevent browser CORS blocks when loading GeoJSON files:
   ```bash
   python3 -m http.server 8080
   ```
   Now, open `http://localhost:8080` in your web browser.

---

## Project Structure

- **Portal Front-End**: 
  - `index.html` — The structural layout for the tabbed dashboard.
  - `real_estate_portal.js` — Core logical script. Manages verified listings database, MapLibre GL cadastral vector overlays, interactive graphs, SRO simulation tickers, and tax calculator.
  - `real_estate_styles.css` — Premium dark-mode styling and listings card grids.
- **Root Datasets**: Cleaned geographic files are stored under `data/andhra_pradesh/` and `data/telangana/`.
- **Scraper scripts**: Located in `scraper/`. Used for raw data collection and compilation from the Local Government Directory (LGD).

---

## Pull Request Guidelines

1. Branch off `main` (e.g., `feat/add-listing-sort`, `fix/maplibre-error`).
2. Implement clean code following existing conventions:
   - Use plain Vanilla CSS and Vanilla Javascript in the root portal.
   - Comment code cleanly.
3. Commit using clear, imperative messages with a type prefix: `feat:`, `fix:`, `docs:`, `chore:`.
4. Ensure files are properly formatted before opening a PR:
   - Run Prettier to format JS, CSS, and HTML.
5. Submit your PR for review. A maintainer will review and test before merging.
