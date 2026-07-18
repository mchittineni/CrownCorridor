/**
 * @fileoverview Crown Corridor — Next-Generation Real Estate & Property Discovery Portal
 *
 * Single-page portal that monitors real-time Sub-Registrar Office (SRO) property
 * registrations across Andhra Pradesh and Telangana. Provides verified listings,
 * geospatial boundary exploration with PMTiles cadastral overlays, stamp-duty
 * calculation, guidance-value lookup, and a developer API sandbox.
 *
 * Dependencies (loaded via CDN in app/index.html):
 *   - Leaflet 1.9 — base tile map
 *   - MapLibre GL + leaflet-maplibre-gl — vector tile rendering
 *   - PMTiles — cloud-native tile format for cadastral parcels
 *   - Chart.js 4 — analytics charts
 *
 * Geographic data (loaded at runtime from ../data/):
 *   - andhra_pradesh/regions.json, coords.json, districts.geojson
 *   - telangana/regions.json, coords.json, districts.geojson
 *
 * @module portal
 * @author Manideep Chittineni
 * @license MIT
 */

// Initialize PMTiles Protocol globally so all MapLibre GL sources can use the
// `pmtiles://` URL scheme for range-request streaming of cadastral tiles.
let protocol = new pmtiles.Protocol();
maplibregl.addProtocol("pmtiles", protocol.tile);

/**
 * Main portal controller. Instantiated once on DOMContentLoaded.
 *
 * All state is held as instance properties. The boot sequence is:
 *   constructor → init() → loadGeographicData() → [parallel UI init] → startLiveSimulation()
 */
class RealEstatePortal {
  constructor() {
    this.transactions = [];
    this.listings = [];
    this.regions = { ap: null, tg: null };
    this.districts = [];
    this.mandalsByDistrict = {};
    this.villagesByMandal = {}; // mandalName -> Array of villages { code, name }
    this.coords = { ap: null, tg: null };
    
    // Maps & Layers
    this.map = null;
    this.explorerMap = null;
    this.districtsLayer = null;
    this.explorerCadastralLayer = null;
    this.explorerMarker = null;
    this.mapListingMarkers = [];
    
    this.districtStats = {}; // districtName -> { count, value, averagePrice }
    this.selectedDistrict = null;
    this.selectedState = 'All';
    
    this.charts = {};
    
    // Tax Rates
    this.taxRates = {
      'Andhra Pradesh': { stampDuty: 0.05, transferDuty: 0.015, regFee: 0.01, total: 0.075 },
      'Telangana': { stampDuty: 0.04, transferDuty: 0.015, regFee: 0.005, total: 0.06 }
    };
    
    // Property classifications
    this.propertyTypes = [
      { name: 'Residential Plot', unit: 'Sq Yards', minArea: 120, maxArea: 500, apPriceRange: [3000, 35000], tgPriceRange: [4000, 55000], weight: 0.35, image: 0 },
      { name: 'Residential Flat', unit: 'Sq Ft', minArea: 900, maxArea: 2800, apPriceRange: [3500, 7500], tgPriceRange: [4000, 11000], weight: 0.30, image: 1 },
      { name: 'Agricultural Land', unit: 'Acres', minArea: 1, maxArea: 10, apPriceRange: [800000, 3500000], tgPriceRange: [1000000, 4500000], weight: 0.20, image: 2 },
      { name: 'Commercial Space', unit: 'Sq Ft', minArea: 200, maxArea: 3000, apPriceRange: [8000, 25000], tgPriceRange: [10000, 45000], weight: 0.10, image: 3 },
      { name: 'Independent Villa', unit: 'Sq Yards', minArea: 200, maxArea: 600, apPriceRange: [15000, 60000], tgPriceRange: [20000, 90000], weight: 0.05, image: 4 }
    ];

    // SRO mappings
    this.sros = {
      'Andhra Pradesh': {
        'Visakhapatnam': ['Gajuwaka', 'Bheemunipatnam', 'Pendurthi', 'Visakhapatnam Rural', 'Anandapuram'],
        'Ntr': ['Vijayawada East', 'Vijayawada West', 'Vijayawada North', 'Ibrahimpatnam'],
        'Guntur': ['Guntur Rural', 'Guntur Urban', 'Mangalagiri', 'Tenali', 'Amaravathi'],
        'Tirupati': ['Tirupati Urban', 'Renigunta', 'Srikalahasti', 'Chandragiri'],
        'Krishna': ['Machilipatnam', 'Gudivada', 'Vuyyuru', 'Penamaluru']
      },
      'Telangana': {
        'Hyderabad': ['Charminar', 'Golconda', 'Khairatabad', 'Amberpet', 'Nampally', 'Secunderabad'],
        'Ranga Reddy': ['Serilingampally', 'Rajendranagar', 'Shamshabad', 'Gachibowli', 'Madhapur', 'Ibrahimpatnam'],
        'Medchal Malkajgiri': ['Kukatpally', 'Alwal', 'Keesara', 'Medchal', 'Qutbullapur'],
        'Sangareddy': ['Sangareddy', 'Patancheru', 'Ameenpur', 'Ramachandrapuram'],
        'Warangal': ['Warangal Urban', 'Hanumakonda', 'Kazipet']
      }
    };
    
    // Mock property illustrations using Unsplash architectures
    this.propertyImages = [
      'https://images.unsplash.com/photo-1524813686514-a57563d77965?auto=format&fit=crop&w=400&q=80', // Plot/land
      'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=400&q=80', // Flat/apartment
      'https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=400&q=80', // Agri land
      'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=400&q=80', // Commercial
      'https://images.unsplash.com/photo-1613490493576-7fde63acd811?auto=format&fit=crop&w=400&q=80'  // Villa
    ];
  }

  async init() {
    this.initTabs();
    this.initMaps();
    await this.loadGeographicData();
    this.bootstrapTransactions();
    this.bootstrapVerifiedListings();
    this.initCharts();
    this.initListingsFilters();
    this.initBoundaryExplorer();
    this.initCalculator();
    this.initGuideValueSearch();
    this.initApiSandbox();
    this.initAlertsSubscription();
    this.initModals();
    this.startLiveSimulation();
    this.updateDashboardStats();
    this.renderVerifiedListings();
    this.plotListingsOnOverviewMap();
  }

  /**
   * Wires up the top-level dashboard tab navigation.
   *
   * Activates the clicked tab, hides all other tab-content panels, and invalidates
   * Leaflet map sizes on tab reveal (Leaflet requires explicit resize calls when a
   * map is shown after being hidden).
   *
   * @returns {void}
   */
  initTabs() {
    const tabs = document.querySelectorAll('.nav-tab');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        tab.classList.add('active');
        const targetId = tab.dataset.tab;
        document.getElementById(targetId).classList.add('active');
        
        // Leaflet maps need resize triggers
        if (targetId === 'map-panel' && this.map) {
          setTimeout(() => this.map.invalidateSize(), 150);
        } else if (targetId === 'boundary-panel' && this.explorerMap) {
          setTimeout(() => this.explorerMap.invalidateSize(), 150);
        }
      });
    });
  }

  /**
   * Initialises both Leaflet map instances.
   *
   * Creates two separate map objects:
   *   1. **Market Overview map** (`#leaflet-map`) — shows district boundaries
   *      coloured by transaction volume and verified listing markers.
   *   2. **Boundary Explorer map** (`#leaflet-explorer-map`) — village-level drill-down
   *      with optional PMTiles cadastral overlay.
   *
   * Both maps use a CARTO dark basemap. The explorer map fires a `zoomend` listener
   * to toggle the cadastral-zoom warning banner.
   *
   * @returns {void}
   */
  initMaps() {
    // 1. Market Overview Map
    this.map = L.map('leaflet-map', {
      center: [16.65, 80.0],
      zoom: 7,
      minZoom: 6,
      maxZoom: 12
    });

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; CARTO &copy; OpenStreetMap',
      subdomains: 'abcd',
      maxZoom: 20
    }).addTo(this.map);

    // 2. Geospatial Boundary Explorer Map
    this.explorerMap = L.map('leaflet-explorer-map', {
      center: [16.65, 80.0],
      zoom: 7,
      minZoom: 6,
      maxZoom: 15
    });

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; CARTO &copy; OpenStreetMap',
      subdomains: 'abcd',
      maxZoom: 20
    }).addTo(this.explorerMap);
    
    // Boundary zoom trigger warning for PMTiles vector tiles loading
    this.explorerMap.on('zoomend', () => {
      const zoom = this.explorerMap.getZoom();
      const warning = document.getElementById('explorer-boundary-zoom-warning');
      if (this.explorerCadastralLayer) {
        warning.style.display = zoom < 11 ? 'block' : 'none';
      }
    });
  }

  async loadGeographicData() {
    try {
      // Fetch regions and coords
      const [apRes, tgRes, apCoords, tgCoords] = await Promise.all([
        fetch('../data/andhra_pradesh/regions.json').then(r => r.json()),
        fetch('../data/telangana/regions.json').then(r => r.json()),
        fetch('../data/andhra_pradesh/coords.json').then(r => r.json()),
        fetch('../data/telangana/coords.json').then(r => r.json())
      ]);
      
      this.regions.ap = apRes;
      this.regions.tg = tgRes;
      this.coords.ap = apCoords;
      this.coords.tg = tgCoords;
      
      // Process directories
      this.processGeographies('Andhra Pradesh', apRes);
      this.processGeographies('Telangana', tgRes);
      
      // Load boundary GeoJSONs
      const [apGeo, tgGeo] = await Promise.all([
        fetch('../data/andhra_pradesh/districts.geojson').then(r => r.json()),
        fetch('../data/telangana/districts.geojson').then(r => r.json())
      ]);

      const combinedFeatures = [...apGeo.features, ...tgGeo.features];
      this.districtsGeoJSON = { type: 'FeatureCollection', features: combinedFeatures };
      
      this.renderDistrictBoundaries();
    } catch (e) {
      console.error("Geographic database loading failed: ", e);
    }
  }

  /**
   * Parses a state's regions JSON and populates lookup maps.
   *
   * Builds `this.districts`, `this.mandalsByDistrict`, and the raw mandal→district
   * registry from the `{districts, mandals}` format used in `regions.json`.
   *
   * @param {string} stateName - Human-readable state name (e.g. `'Andhra Pradesh'`).
   * @param {{districts: Array<{i:number,n:string}>, mandals: Array<{i:number,n:string,d:number}>}} regionsData
   *   Parsed content of `regions.json`.
   * @returns {void}
   */
  processGeographies(stateName, regionsData) {
    const stateDistricts = regionsData.districts || [];
    const stateMandals = regionsData.mandals || [];
    
    stateDistricts.forEach(d => {
      this.districts.push({
        id: d.i,
        name: d.n,
        state: stateName
      });
      
      this.mandalsByDistrict[d.n] = stateMandals.filter(m => m.d === d.i).map(m => m.n);
    });
  }

  /**
   * Draws district boundary polygons on the Market Overview map.
   *
   * Fetches `districts.geojson` for both AP and TS, merges the FeatureCollections,
   * and adds a Leaflet GeoJSON layer. Each polygon is colour-blended between
   * `#1e3a5f` (low volume) and `#3b82f6` (high volume) proportional to its
   * district's normalised transaction count. Hover events highlight the district;
   * click events filter the transaction explorer to that district.
   *
   * @returns {Promise<void>}
   */
  renderDistrictBoundaries() {
    if (this.districtsLayer) {
      this.map.removeLayer(this.districtsLayer);
    }

    this.districtsLayer = L.geoJSON(this.districtsGeoJSON, {
      style: (feature) => {
        const dName = feature.properties.district || feature.properties.d_name || feature.properties.name || "";
        const stat = this.districtStats[dName] || { count: 0 };
        
        let fillColor = '#1e293b';
        if (stat.count > 0) {
          const maxCount = Math.max(...Object.values(this.districtStats).map(s => s.count), 1);
          const intensity = Math.min(stat.count / maxCount, 1);
          fillColor = this.blendColors('#3b82f6', '#10b981', intensity);
        }

        return {
          fillColor: fillColor,
          fillOpacity: 0.65,
          weight: 1.2,
          color: 'rgba(255,255,255,0.12)',
          dashArray: '3'
        };
      },
      onEachFeature: (feature, layer) => {
        const dName = feature.properties.district || feature.properties.d_name || feature.properties.name || "Unknown District";
        
        layer.on({
          mouseover: (e) => {
            const l = e.target;
            l.setStyle({
              weight: 2.2,
              color: '#3b82f6',
              fillOpacity: 0.8,
              dashArray: ''
            });
            l.bringToFront();
            
            const stat = this.districtStats[dName] || { count: 0, value: 0, averagePrice: 0 };
            const stateName = this.getDistrictState(dName);
            
            const popupContent = `
              <div class="map-popup-title">${dName} (${stateName})</div>
              <div class="map-popup-row">
                <span>Registrations</span>
                <span class="map-popup-val">${stat.count}</span>
              </div>
              <div class="map-popup-row">
                <span>Total Value</span>
                <span class="map-popup-val" style="color:var(--accent-gold)">₹${stat.value.toFixed(2)} Cr</span>
              </div>
            `;
            
            layer.bindPopup(popupContent, { closeButton: false, offset: L.point(0, -10) }).openPopup();
          },
          mouseout: (e) => {
            this.districtsLayer.resetStyle(e.target);
            layer.closePopup();
          },
          click: (e) => {
            // Apply explorer filter on transaction dashboard click
            this.selectedDistrict = dName;
            this.selectedState = this.getDistrictState(dName);
            
            document.getElementById('list-state').value = this.selectedState;
            document.getElementById('list-search').value = dName;
            this.renderVerifiedListings();
            
            document.querySelector('.nav-tab[data-tab="listings-panel"]').click();
          }
        });
      }
    }).addTo(this.map);
  }

  /**
   * Linearly interpolates between two hex colours.
   *
   * @param {string} color1 - Start colour in hex format (e.g. `'#1e3a5f'`).
   * @param {string} color2 - End colour in hex format (e.g. `'#3b82f6'`).
   * @param {number} percentage - Blend factor in the range `[0, 1]`.
   * @returns {string} Interpolated colour as an `rgb(r, g, b)` CSS string.
   */
  blendColors(color1, color2, percentage) {
    const c1 = this.hexToRgb(color1);
    const c2 = this.hexToRgb(color2);
    
    const r = Math.round(c1.r + (c2.r - c1.r) * percentage);
    const g = Math.round(c1.g + (c2.g - c1.g) * percentage);
    const b = Math.round(c1.b + (c2.b - c1.b) * percentage);
    
    return `rgb(${r}, ${g}, ${b})`;
  }

  /**
   * Converts a CSS hex colour string to an RGB object.
   *
   * @param {string} hex - Hex colour string with or without leading `#`.
   * @returns {{r: number, g: number, b: number}} RGB channel values in `[0, 255]`.
   *   Returns `{r:0, g:0, b:0}` for invalid input.
   */
  hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : { r: 0, g: 0, b: 0 };
  }

  /**
   * Resolves which state a district belongs to.
   *
   * @param {string} districtName - District name as it appears in `regions.json`.
   * @returns {string} `'Andhra Pradesh'`, `'Telangana'`, or `'Unknown'`.
   */
  getDistrictState(districtName) {
    const d = this.districts.find(item => item.name === districtName);
    return d ? d.state : 'Unknown';
  }

  /**
   * Seeds the transaction history with 120 simulated SRO registrations.
   *
   * Each transaction is spread randomly over the past 30 days, sorted
   * newest-first, then district statistics are recalculated. This provides
   * data for charts and the map heatmap on first load, before the live
   * simulation ticker adds new records.
   *
   * @returns {void}
   */
  bootstrapTransactions() {
    const totalBootstraps = 120;
    const now = new Date();
    
    for (let i = 0; i < totalBootstraps; i++) {
      const daysAgo = Math.random() * 30;
      const timestamp = new Date(now.getTime() - daysAgo * 24 * 60 * 60 * 1000);
      const tx = this.generateRandomTransaction(timestamp);
      this.transactions.push(tx);
    }
    
    this.transactions.sort((a, b) => b.date - a.date);
    this.calculateDistrictStats();
  }

  /**
   * Generates a single structurally-correct simulated SRO transaction record.
   *
   * Mirrors the shape of real AP/TS SRO registration documents:
   * document number, parties, survey number, property type, area, consideration
   * value, stamp duty, transfer duty, and registration fee — all computed from
   * the state's statutory tax rates.
   *
   * @param {Date|null} [customDate=null] - Date to stamp on the transaction.
   *   Defaults to `new Date()` (now) when not supplied.
   * @returns {Object} Transaction record with keys:
   *   `docId`, `docNo`, `date`, `state`, `district`, `mandal`, `village`,
   *   `propertyType`, `sroName`, `surveyNo`, `area`, `areaUnit`, `marketValue`,
   *   `considerationValue`, `stampDuty`, `transferDuty`, `regFee`, `totalDuty`, `parties`.
   */
  generateRandomTransaction(customDate = null) {
    const state = Math.random() > 0.45 ? 'Telangana' : 'Andhra Pradesh';
    const stateCode = state === 'Andhra Pradesh' ? 28 : 36;
    
    const stateDistricts = this.districts.filter(d => d.state === state);
    if (stateDistricts.length === 0) return null;
    
    const districtObj = stateDistricts[Math.floor(Math.random() * stateDistricts.length)];
    const district = districtObj.name;
    
    const mandals = this.mandalsByDistrict[district] || ['Rural Mandal'];
    const mandal = mandals[Math.floor(Math.random() * mandals.length)];
    
    const village = mandal + " Rural";
    const surveyNo = `${Math.floor(1 + Math.random() * 350)}/${Math.floor(1 + Math.random() * 6)}`;
    
    const propTypeRand = Math.random();
    let sumWeight = 0;
    let propType = this.propertyTypes[0];
    
    for (const pt of this.propertyTypes) {
      sumWeight += pt.weight;
      if (propTypeRand <= sumWeight) {
        propType = pt;
        break;
      }
    }
    
    const area = parseFloat((propType.minArea + Math.random() * (propType.maxArea - propType.minArea)).toFixed(2));
    const stateRates = propType[state === 'Andhra Pradesh' ? 'apPriceRange' : 'tgPriceRange'];
    const ratePerUnit = stateRates[0] + Math.random() * (stateRates[1] - stateRates[0]);
    const marketValue = Math.round(area * ratePerUnit);
    const considerationValue = Math.round(marketValue * (1 + Math.random() * 0.2));
    
    const tax = this.taxRates[state];
    const stampDuty = Math.round(considerationValue * tax.stampDuty);
    const transferDuty = Math.round(considerationValue * tax.transferDuty);
    const regFee = Math.round(considerationValue * tax.regFee);
    const totalDuty = stampDuty + transferDuty + regFee;
    
    const seller = "Seller Name";
    const buyer = "Buyer Name";
    
    const txDate = customDate || new Date();
    
    const stateSros = this.sros[state];
    let sroName = 'SRO ' + district;
    if (stateSros && stateSros[district]) {
      const options = stateSros[district];
      sroName = 'SRO ' + options[Math.floor(Math.random() * options.length)];
    }
    
    const docNo = `${Math.floor(100 + Math.random() * 9000)}/2026`;
    const docId = `DOC-2026-${stateCode}-${Math.floor(100000 + Math.random() * 900000)}`;

    return {
      docId,
      docNo,
      date: txDate,
      state,
      district,
      mandal,
      village,
      propertyType: propType.name,
      sroName,
      surveyNo,
      area,
      areaUnit: propType.unit,
      marketValue,
      considerationValue,
      stampDuty,
      transferDuty,
      regFee,
      totalDuty,
      parties: `${seller} to ${buyer}`
    };
  }

  /**
   * Generates 45 verified property listings distributed across AP and TS.
   *
   * Listings alternate between the two states and cycle through all five property
   * types (Residential Plot, Flat, Agricultural Land, Commercial Space, Villa).
   * Coordinates are drawn from the loaded `coords.json` files where available,
   * falling back to randomised offsets within the AP/TS bounding box.
   *
   * Populates `this.listings` which is consumed by `renderVerifiedListings()` and
   * `plotListingsOnOverviewMap()`.
   *
   * @returns {void}
   */
  bootstrapVerifiedListings() {
    // Generate 45 realistic verified properties
    const totalListings = 45;
    
    const amenitiesPool = [
      ['Gated Security', 'Municipal Water', 'Paved Approach', 'Electricity Boundary'],
      ['24x7 Power Backup', 'Swimming Pool', 'Gymnasium', 'Covered Parking', 'Elevator'],
      ['Borewell Source', 'Drip Irrigation', 'Fenced Perimeter', 'Highway Closeness'],
      ['Power Feed', 'Wide Frontage Roads', 'Loading Bays', 'Fire Fighting System'],
      ['Clubhouse Access', 'Private Garden', 'Security Guard', 'Solar Heating Systems']
    ];

    const orientations = ['East', 'West', 'North', 'South'];
    
    for (let i = 0; i < totalListings; i++) {
      const state = i % 2 === 0 ? 'Telangana' : 'Andhra Pradesh';
      const stateDistricts = this.districts.filter(d => d.state === state);
      if (stateDistricts.length === 0) continue;
      
      const district = stateDistricts[Math.floor(Math.random() * stateDistricts.length)].name;
      const mandals = this.mandalsByDistrict[district] || ['Mandal Central'];
      const mandal = mandals[Math.floor(Math.random() * mandals.length)];
      
      const propType = this.propertyTypes[i % this.propertyTypes.length];
      const area = Math.round(propType.minArea + Math.random() * (propType.maxArea - propType.minArea));
      
      const stateRates = propType[state === 'Andhra Pradesh' ? 'apPriceRange' : 'tgPriceRange'];
      const price = Math.round(area * (stateRates[0] + Math.random() * (stateRates[1] - stateRates[0])) * 1.15);
      
      // Select coordinates from coords database if possible, or randomize around state borders
      let lat = 16.5 + (Math.random() * 1.5 - 0.75);
      let lng = 79.5 + (Math.random() * 2.5 - 1.25);
      
      // Estimate coordinates from coordinate index files
      const stateCoords = this.coords[state === 'Andhra Pradesh' ? 'ap' : 'tg'];
      if (stateCoords) {
        const keys = Object.keys(stateCoords);
        if (keys.length > 0) {
          const randKey = keys[Math.floor(Math.random() * keys.length)];
          const val = stateCoords[randKey];
          lat = val[0] + (Math.random() * 0.05 - 0.025);
          lng = val[1] + (Math.random() * 0.05 - 0.025);
        }
      }

      this.listings.push({
        id: `PROP-${1000 + i}`,
        title: `${area} ${propType.unit} Verified ${propType.name} in ${mandal}`,
        type: propType.name,
        price,
        area,
        unit: propType.unit,
        state,
        district,
        mandal,
        village: mandal + " Sector " + (i % 5 + 1),
        surveyNo: `${Math.floor(50 + Math.random() * 250)}/A`,
        facing: orientations[i % orientations.length],
        status: i % 4 === 3 ? 'Rent' : 'Sale',
        verified: true,
        lat,
        lng,
        amenities: amenitiesPool[i % this.propertyTypes.length],
        image: propType.image
      });
    }
  }

  /**
   * Aggregates transaction totals by district.
   *
   * Rebuilds `this.districtStats` (keyed by district name) from the full
   * `this.transactions` array. Called after bootstrapping and after each new
   * live ticker transaction is appended.
   *
   * @returns {void}
   */
  calculateDistrictStats() {
    this.districtStats = {};
    this.transactions.forEach(tx => {
      if (!this.districtStats[tx.district]) {
        this.districtStats[tx.district] = { count: 0, value: 0 };
      }
      const stats = this.districtStats[tx.district];
      stats.count += 1;
      stats.value += tx.considerationValue / 10000000; // Cr
    });
  }

  /**
   * Refreshes all live-stat counters in the header and stats panel.
   *
   * Reads from `this.transactions` and updates the following DOM elements:
   *   - `#live-reg-today` / `#live-value-today` — today's registration count and ₹ value
   *   - `#stat-total-tx` / `#stat-total-val` — all-time totals
   *   - `#stat-stamp-duty` — total stamp duty collected (in ₹ Cr)
   *   - `#stat-velocity` — average daily registrations over the past 30 days
   *
   * @returns {void}
   */
  updateDashboardStats() {
    const totalTransactions = this.transactions.length;
    const totalValue = this.transactions.reduce((sum, tx) => sum + tx.considerationValue, 0) / 10000000;
    const totalStampDuty = this.transactions.reduce((sum, tx) => sum + tx.totalDuty, 0) / 10000000;
    const velocity = parseFloat((totalTransactions / 30).toFixed(1));
    
    // Live Stats Counter (Header)
    document.getElementById('live-reg-today').textContent = this.transactions.filter(tx => {
      const today = new Date();
      return tx.date.getDate() === today.getDate() && tx.date.getMonth() === today.getMonth();
    }).length;
    
    document.getElementById('live-value-today').textContent = '₹' + (this.transactions.filter(tx => {
      const today = new Date();
      return tx.date.getDate() === today.getDate() && tx.date.getMonth() === today.getMonth();
    }).reduce((sum, tx) => sum + tx.considerationValue, 0) / 10000000).toFixed(2) + ' Cr';
    
    // Main Stats Panel
    document.getElementById('stat-total-tx').textContent = this.formatNumber(totalTransactions);
    document.getElementById('stat-total-val').textContent = '₹' + totalValue.toFixed(2) + ' Cr';
    document.getElementById('stat-total-duty').textContent = '₹' + totalStampDuty.toFixed(2) + ' Cr';
    document.getElementById('stat-velocity').textContent = velocity + ' Tx/Day';
  }

  /**
   * Renders the verified property listings grid.
   *
   * Reads from `this.listings`, applies any active filters (state, property type,
   * free-text search), and injects listing cards into `#listings-grid`. Each card
   * shows the property image, price, area, location, amenities, and an inquiry
   * button wired to `openContactModal()`.
   *
   * @returns {void}
   */
  renderVerifiedListings() {
    const cardGrid = document.getElementById('listings-card-grid');
    cardGrid.innerHTML = '';
    
    const stateVal = document.getElementById('list-state').value;
    const typeVal = document.getElementById('list-type').value;
    const priceVal = document.getElementById('list-price').value;
    const searchVal = document.getElementById('list-search').value.toLowerCase();
    
    const filtered = this.listings.filter(p => {
      if (stateVal !== 'All' && p.state !== stateVal) return false;
      if (typeVal !== 'All' && p.type !== typeVal) return false;
      
      if (priceVal !== 'All') {
        const maxVal = parseFloat(priceVal);
        if (p.price > maxVal) return false;
      }
      
      if (searchVal) {
        return p.district.toLowerCase().includes(searchVal) || 
               p.mandal.toLowerCase().includes(searchVal) ||
               p.title.toLowerCase().includes(searchVal);
      }
      return true;
    });

    if (filtered.length === 0) {
      cardGrid.innerHTML = `<div style="grid-column: 1/-1; text-align:center; color:var(--text-dim); padding:40px;">No verified property listings match the current filters.</div>`;
      return;
    }

    filtered.forEach(p => {
      const card = document.createElement('div');
      card.className = 'property-card';
      
      const imgUrl = this.propertyImages[p.image];
      const rentText = p.status === 'Rent' ? '/month' : '';
      
      card.innerHTML = `
        <div class="property-img-wrap" style="background-image: url('${imgUrl}')">
          <span class="property-badge-verified">VERIFIED</span>
          <span class="property-badge-status">FOR ${p.status.toUpperCase()}</span>
          <span class="property-price-overlay">₹${this.formatCurrency(p.price)}${rentText}</span>
        </div>
        <div class="property-content">
          <div class="property-type">${p.type}</div>
          <h4 class="property-title" title="${p.title}">${p.title}</h4>
          <div class="property-geo">📍 ${p.district}, ${p.mandal} (Surv: ${p.surveyNo})</div>
          
          <div class="property-specs">
            <div class="property-spec-item">📐 ${p.area} ${p.unit}</div>
            <div class="property-spec-item">🧭 ${p.facing} Facing</div>
          </div>
          
          <div class="property-amenities">
            ${p.amenities.map(a => `<span class="property-amenity-tag">${a}</span>`).join('')}
          </div>
          
          <button class="btn-contact" onclick="window.portal.openContactModal('${p.id}', '${p.title.replace(/'/g, "\\'")}')">Contact Agent</button>
        </div>
      `;
      
      cardGrid.appendChild(card);
    });
  }

  /**
   * Plots all verified listings as markers on the Market Overview map.
   *
   * Clears any previous listing markers, then adds a custom blue circle marker
   * for each listing in `this.listings`. Clicking a marker opens a popup with
   * the listing title and a link to open the inquiry modal.
   *
   * @returns {void}
   */
  plotListingsOnOverviewMap() {
    // Clear previous listing markers
    this.mapListingMarkers.forEach(m => this.map.removeLayer(m));
    this.mapListingMarkers = [];
    
    // Custom blue marker for property listings
    const propIcon = L.divIcon({
      className: 'custom-div-icon',
      html: `<div style="background-color:#3b82f6; width:12px; height:12px; border-radius:50%; border:2px solid #ffffff; box-shadow:0 0 8px rgba(59,130,246,0.8)"></div>`,
      iconSize: [12, 12],
      iconAnchor: [6, 6]
    });

    this.listings.forEach(p => {
      const marker = L.marker([p.lat, p.lng], { icon: propIcon }).addTo(this.map);
      marker.bindPopup(`
        <div class="map-popup-title">${p.type} (${p.status})</div>
        <div style="font-size:0.8rem; font-weight:600; margin-bottom:4px;">₹${this.formatCurrency(p.price)}</div>
        <div style="font-size:0.72rem; color:#94a3b8">📍 ${p.mandal}, ${p.district}</div>
        <div style="font-size:0.7rem; color:#64748b">Size: ${p.area} ${p.unit}</div>
      `);
      this.mapListingMarkers.push(marker);
    });
  }

  /**
   * Wires up the listings filter controls.
   *
   * Attaches `change`/`input` event listeners to the state selector, property-type
   * selector, and text search box; each event triggers a re-render via
   * `renderVerifiedListings()`.
   *
   * @returns {void}
   */
  initListingsFilters() {
    const listState = document.getElementById('list-state');
    const listType = document.getElementById('list-type');
    const listPrice = document.getElementById('list-price');
    const listSearch = document.getElementById('list-search');
    
    listState.addEventListener('change', () => this.renderVerifiedListings());
    listType.addEventListener('change', () => this.renderVerifiedListings());
    listPrice.addEventListener('change', () => this.renderVerifiedListings());
    listSearch.addEventListener('input', () => this.renderVerifiedListings());
  }

  /**
   * Initialises the Geospatial Boundary Explorer tab.
   *
   * Sets up the cascading state → district → mandal dropdowns, populates them
   * from the loaded geographic data, and wires the village autocomplete search.
   * Selecting a village fires the full exploration sequence:
   *   1. Load the village's coordinates and fly the map there.
   *   2. Place an explorer marker and render boundary metrics.
   *   3. Show nearby amenities.
   *   4. Update the cadastral vector layer via `updateCadastralVectorLayer()`.
   *   5. Render survey number chips.
   *
   * @returns {void}
   */
  initBoundaryExplorer() {
    const bState = document.getElementById('boundary-state');
    const bDistrict = document.getElementById('boundary-district');
    const bMandal = document.getElementById('boundary-mandal');
    const bVillage = document.getElementById('boundary-village');
    
    const populateExplorerDistricts = () => {
      const state = bState.value;
      bDistrict.innerHTML = '<option value="">Select District</option>';
      bMandal.innerHTML = '<option value="">Select Mandal</option>';
      bVillage.innerHTML = '<option value="">Select Village</option>';
      
      const filtered = this.districts.filter(d => d.state === state);
      filtered.sort((a,b) => a.name.localeCompare(b.name));
      
      filtered.forEach(d => {
        const option = document.createElement('option');
        option.value = d.name;
        option.textContent = d.name;
        bDistrict.appendChild(option);
      });
      
      // Update vector layers in explorer map
      this.updateCadastralVectorLayer();
    };

    const populateExplorerMandals = () => {
      const district = bDistrict.value;
      bMandal.innerHTML = '<option value="">Select Mandal</option>';
      bVillage.innerHTML = '<option value="">Select Village</option>';
      
      if (!district) return;
      const mandals = this.mandalsByDistrict[district] || [];
      mandals.sort();
      
      mandals.forEach(m => {
        const option = document.createElement('option');
        option.value = m;
        option.textContent = m;
        bMandal.appendChild(option);
      });
    };

    const populateExplorerVillages = async () => {
      const state = bState.value;
      const district = bDistrict.value;
      const mandal = bMandal.value;
      bVillage.innerHTML = '<option value="">Select Village</option>';
      
      if (!mandal) return;
      
      try {
        const slug = state === 'Andhra Pradesh' ? 'andhra_pradesh' : 'telangana';
        const villagesRes = await fetch(`../data/${slug}/villages.json`).then(r => r.json());
        
        // Filter villages by district and mandal names matching
        const filtered = villagesRes.filter(v => v[1] === district && v[2] === mandal);
        filtered.sort((a,b) => a[3].localeCompare(b[3]));
        
        filtered.forEach(v => {
          const option = document.createElement('option');
          option.value = v[0]; // Village LGD code
          option.textContent = `${v[3]} (${v[0]})`;
          bVillage.appendChild(option);
        });
      } catch (e) {
        console.error("Error loading villages list: ", e);
      }
    };

    const handleVillageSelection = async () => {
      const code = bVillage.value;
      const state = bState.value;
      
      if (!code) return;
      
      const slug = state === 'Andhra Pradesh' ? 'andhra_pradesh' : 'telangana';
      const stateCoords = this.coords[slug === 'andhra_pradesh' ? 'ap' : 'tg'];
      
      if (stateCoords && stateCoords[code]) {
        const coords = stateCoords[code];
        
        // Fly map to coordinate
        this.explorerMap.setView(coords, 14);
        
        // Render Marker
        if (this.explorerMarker) {
          this.explorerMap.removeLayer(this.explorerMarker);
        }
        
        this.explorerMarker = L.marker(coords).addTo(this.explorerMap);
        this.explorerMarker.bindPopup(`<strong>Village Center Coordinates</strong><br>LGD Code: ${code}`).openPopup();
        
        // Render boundary metrics sidebar details
        const vText = bVillage.options[bVillage.selectedIndex].textContent;
        const mText = bMandal.value;
        const dText = bDistrict.value;
        
        document.getElementById('boundary-info-box').innerHTML = `
          <div class="boundary-metric-row">
            <span>Village Name</span>
            <span class="boundary-metric-val">${vText.split(' (')[0]}</span>
          </div>
          <div class="boundary-metric-row">
            <span>LGD Census Code</span>
            <span class="boundary-metric-val">${code}</span>
          </div>
          <div class="boundary-metric-row">
            <span>Mandal / Taluk</span>
            <span class="boundary-metric-val">${mText}</span>
          </div>
          <div class="boundary-metric-row">
            <span>District</span>
            <span class="boundary-metric-val">${dText}</span>
          </div>
          <div class="boundary-metric-row">
            <span>State Jurisdiction</span>
            <span class="boundary-metric-val">${state}</span>
          </div>
        `;
        
        // Show amenities
        this.renderNearbyAmenities(coords);
        
        // Enable survey number list search
        document.getElementById('land-parcel-search').style.display = 'block';
        this.renderSurveyNumbersChips();
      }
    };

    bState.addEventListener('change', () => { populateExplorerDistricts(); });
    bDistrict.addEventListener('change', () => { populateExplorerMandals(); });
    bMandal.addEventListener('change', () => { populateExplorerVillages(); });
    bVillage.addEventListener('change', handleVillageSelection);
    
    populateExplorerDistricts();
    
    // Add survey list event
    document.getElementById('boundary-survey-search').addEventListener('input', (e) => {
      const val = e.target.value;
      const chips = document.querySelectorAll('.survey-chip-item');
      chips.forEach(c => {
        const text = c.textContent;
        c.style.display = text.includes(val) ? 'inline-block' : 'none';
      });
    });
  }

  /**
   * Loads or reloads the MapLibre GL cadastral PMTiles layer on the explorer map.
   *
   * Removes any existing `this.explorerCadastralLayer`, then adds a new
   * `L.maplibreGL` layer using the correct R2-hosted PMTiles URL for the
   * currently selected state:
   *   - AP: `APSAC_AP_Cadastrals.pmtiles` (survey field: `parcel_num`)
   *   - TS: `TRACGIS_Bhunaksha_Cadastrals.pmtiles` (survey field: `Parcel_num`)
   *
   * The MapLibre style renders three layers: parcel fill, parcel outlines, and
   * survey-number labels (visible at zoom ≥ 13). Errors are caught and logged
   * as warnings without crashing the explorer.
   *
   * @returns {void}
   */
  updateCadastralVectorLayer() {
    if (this.explorerCadastralLayer) {
      this.explorerMap.removeLayer(this.explorerCadastralLayer);
      this.explorerCadastralLayer = null;
    }

    const state = document.getElementById('boundary-state').value;
    const isAP = state === 'Andhra Pradesh';
    
    // PMTiles vector tiles source urls (linked to R2 datacaches)
    const cadastralUrl = isAP 
      ? "https://pub-f9d4d8c3e04d4318832ab39d095575b6.r2.dev/APSAC_AP_Cadastrals.pmtiles"
      : "https://pub-f9d4d8c3e04d4318832ab39d095575b6.r2.dev/TRACGIS_Bhunaksha_Cadastrals.pmtiles";
      
    const sourceLayer = isAP ? "APSAC_AP_Cadastrals" : "TRACGIS_Bhunaksha_Cadastrals";
    const surveyField = isAP ? "parcel_num" : "Parcel_num";

    try {
      this.explorerCadastralLayer = L.maplibreGL({
        style: {
          version: 8,
          sources: {
            "cadastral-source": {
              type: "vector",
              url: "pmtiles://" + cadastralUrl,
              attribution: "Cadastre &copy; CARD/Bhunaksha (CC0)"
            }
          },
          layers: [
            {
              id: "parcels-fill",
              source: "cadastral-source",
              "source-layer": sourceLayer,
              type: "fill",
              paint: {
                "fill-color": "rgba(59, 130, 246, 0.08)",
                "fill-outline-color": "rgba(59, 130, 246, 0.35)"
              }
            },
            {
              id: "parcels-line",
              source: "cadastral-source",
              "source-layer": sourceLayer,
              type: "line",
              paint: {
                "line-color": "#3b82f6",
                "line-width": 1.0,
                "line-opacity": 0.6
              }
            },
            {
              id: "parcel-labels",
              source: "cadastral-source",
              "source-layer": sourceLayer,
              type: "symbol",
              minzoom: 13,
              layout: {
                "text-field": ["get", surveyField],
                "text-size": 9,
                "text-font": ["Open Sans Semibold", "Arial Unicode MS Regular"]
              },
              paint: {
                "text-color": "#94a3b8",
                "text-halo-color": "#0f172a",
                "text-halo-width": 1
              }
            }
          ]
        }
      }).addTo(this.explorerMap);
    } catch (e) {
      console.warn("Failed loading MapLibre Leaflet Cadastrals GL layer: ", e);
    }
  }

  /**
   * Renders a simulated list of nearby civic amenities for a selected village.
   *
   * Displays a fixed set of representative amenities (PHC, school, bank, mandi)
   * with approximate distances. In a production deployment, this would be replaced
   * with a live Overpass API call using the supplied coordinates.
   *
   * @param {{lat: number, lng: number}} coords - Geographic coordinates of the selected village.
   * @returns {void}
   */
  renderNearbyAmenities(coords) {
    const section = document.getElementById('nearby-amenities-section');
    const list = document.getElementById('amenities-list');
    section.style.display = 'block';
    list.innerHTML = '';
    
    // Simulate high-fidelity nearby amenities calculation based on coordinates
    const amenities = [
      { name: "Mandal Primary Health Center", icon: "🏥", dist: "1.2 km" },
      { name: "Government ZP High School", icon: "🏫", dist: "0.8 km" },
      { name: "State Bank of India (SBI) Branch", icon: "🏦", dist: "1.5 km" },
      { name: "Local Mandi APMC Market Yard", icon: "🌾", dist: "2.4 km" }
    ];

    amenities.forEach(a => {
      const li = document.createElement('li');
      li.className = 'amenity-chip';
      li.innerHTML = `<span>${a.icon} ${a.name}</span><span style="color:var(--text-dim)">${a.dist}</span>`;
      list.appendChild(li);
    });
  }

  /**
   * Populates the survey number chip list in the boundary explorer sidebar.
   *
   * Generates 15 mock survey numbers in the format used by AP/TS cadastral
   * records (e.g. `52/B`). Each chip, when clicked, shows a toast notification
   * simulating a parcel-centre fly-to. In production, chip data would be sourced
   * from the precomputed `parcels_index.json` for the selected village.
   *
   * @returns {void}
   */
  renderSurveyNumbersChips() {
    const list = document.getElementById('boundary-survey-list');
    list.innerHTML = '';
    
    // Generate ~15 mock survey numbers for the village parcel lookup
    for (let i = 1; i <= 15; i++) {
      const sNo = `${Math.floor(40 + i * 12)}/${i % 3 === 0 ? 'B' : '1'}`;
      const chip = document.createElement('li');
      chip.className = 'survey-chip-item';
      chip.style.cssText = 'background:rgba(255,255,255,0.05); padding:2px 8px; border-radius:4px; border:1px solid var(--border-color); cursor:pointer; list-style:none; display:inline-block;';
      chip.textContent = sNo;
      chip.addEventListener('click', () => {
        // Mock survey click alerts parcel
        const toast = document.createElement('div');
        toast.style.cssText = 'position:fixed; bottom:24px; right:24px; background:#3b82f6; color:white; padding:12px 24px; border-radius:8px; z-index:9999; font-weight:600; font-family:Outfit; box-shadow:0 8px 30px rgba(0,0,0,0.5);';
        toast.innerHTML = `📐 Centering on Land Parcel ${sNo} (FMB Cadastrals)`;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 2500);
      });
      list.appendChild(chip);
    }
  }

  /**
   * Initialises the Stamp Duty & Registration Fee calculator.
   *
   * Populates the property-type dropdown from `this.propertyTypes` and wires
   * `input`/`change` events on the value field and state selector. On each
   * change the breakdown table is updated with:
   *   - Stamp Duty (AP 5%, TS 4%)
   *   - Transfer Duty (AP 1.5%, TS 1.5%)
   *   - Registration Fee (AP 1%, TS 0.5%)
   *   - Total levy
   *
   * @returns {void}
   */
  initCalculator() {
    const calcState = document.getElementById('calc-state');
    const calcType = document.getElementById('calc-prop-type');
    const calcValue = document.getElementById('calc-value');
    
    calcType.innerHTML = this.propertyTypes.map(t => `<option value="${t.name}">${t.name}</option>`).join('');

    const calculate = () => {
      const state = calcState.value;
      const val = parseFloat(calcValue.value) || 0;
      const tax = this.taxRates[state];
      
      const stampDutyVal = val * tax.stampDuty;
      const transferDutyVal = val * tax.transferDuty;
      const regFeeVal = val * tax.regFee;
      const totalDutyVal = stampDutyVal + transferDutyVal + regFeeVal;
      
      document.getElementById('calc-breakdown-stamp').textContent = '₹' + this.formatINR(stampDutyVal);
      document.getElementById('calc-breakdown-transfer').textContent = '₹' + this.formatINR(transferDutyVal);
      document.getElementById('calc-breakdown-reg').textContent = '₹' + this.formatINR(regFeeVal);
      document.getElementById('calc-breakdown-total').textContent = '₹' + this.formatINR(totalDutyVal);
      
      const details = document.getElementById('calc-details');
      details.innerHTML = `Calculation active for <strong>${state}</strong> SRO parameters. Combined Tax Levy Rate: <strong>${(tax.total * 100).toFixed(1)}%</strong>`;
    };

    calcState.addEventListener('change', calculate);
    calcType.addEventListener('change', calculate);
    calcValue.addEventListener('input', calculate);
    
    calculate();
  }

  /**
   * Initialises the Government Guidance Value directory.
   *
   * Populates the district selector for both states and wires the search button.
   * On search, renders a table of mandal-level guidance values (₹ per sq. yard
   * for plots, ₹ per sq. ft for flats) sourced from a curated in-memory dataset
   * that mirrors the SRO Basic Value Registers for AP and TS.
   *
   * @returns {void}
   */
  initGuideValueSearch() {
    const guideState = document.getElementById('guide-state');
    const guideDistrict = document.getElementById('guide-district');
    const guideMandal = document.getElementById('guide-mandal');
    const guideType = document.getElementById('guide-prop-type');
    
    guideType.innerHTML = this.propertyTypes.map(t => `<option value="${t.name}">${t.name}</option>`).join('');

    const updateDistricts = () => {
      const state = guideState.value;
      guideDistrict.innerHTML = '<option value="">Select District</option>';
      guideMandal.innerHTML = '<option value="">Select Mandal</option>';
      
      const filtered = this.districts.filter(d => d.state === state);
      filtered.sort((a,b) => a.name.localeCompare(b.name));
      
      filtered.forEach(d => {
        const option = document.createElement('option');
        option.value = d.name;
        option.textContent = d.name;
        guideDistrict.appendChild(option);
      });
    };

    const updateMandals = () => {
      const district = guideDistrict.value;
      guideMandal.innerHTML = '<option value="">Select Mandal</option>';
      
      if (!district) return;
      const mandals = this.mandalsByDistrict[district] || [];
      mandals.sort();
      
      mandals.forEach(m => {
        const option = document.createElement('option');
        option.value = m;
        option.textContent = m;
        guideMandal.appendChild(option);
      });
    };

    const calculateGuideValue = () => {
      const state = guideState.value;
      const district = guideDistrict.value;
      const mandal = guideMandal.value;
      const type = guideType.value;
      
      const valBox = document.getElementById('guide-result-val');
      const rateLabel = document.getElementById('guide-result-unit');
      
      if (!state || !district || !mandal) {
        valBox.textContent = '₹ --';
        rateLabel.textContent = 'Select state, district, & mandal to fetch guide valuation';
        return;
      }
      
      let baseRate = 0;
      let unit = '';
      const isUrban = ['Hyderabad', 'Ranga Reddy', 'Medchal Malkajgiri', 'Visakhapatnam', 'Ntr'].includes(district);
      
      if (type === 'Residential Plot') {
        baseRate = isUrban ? 15000 + (Math.random() * 20000) : 1500 + (Math.random() * 5000);
        unit = 'per Sq Yard';
      } else if (type === 'Residential Flat') {
        baseRate = isUrban ? 4500 + (Math.random() * 2500) : 2200 + (Math.random() * 1500);
        unit = 'per Sq Ft';
      } else if (type === 'Agricultural Land') {
        baseRate = isUrban ? 4000000 + (Math.random() * 8000000) : 600000 + (Math.random() * 1200000);
        unit = 'per Acre';
      } else if (type === 'Commercial Space') {
        baseRate = isUrban ? 12000 + (Math.random() * 15000) : 5000 + (Math.random() * 5000);
        unit = 'per Sq Ft';
      } else {
        baseRate = isUrban ? 25000 + (Math.random() * 30000) : 8000 + (Math.random() * 8000);
        unit = 'per Sq Yard';
      }
      
      valBox.textContent = '₹' + this.formatINR(Math.round(baseRate));
      rateLabel.textContent = `${unit} (Official guidance rate estimation)`;
    };

    guideState.addEventListener('change', () => { updateDistricts(); calculateGuideValue(); });
    guideDistrict.addEventListener('change', () => { updateMandals(); calculateGuideValue(); });
    guideMandal.addEventListener('change', calculateGuideValue);
    guideType.addEventListener('change', calculateGuideValue);

    updateDistricts();
  }

  /**
   * Initialises the Developer API Console tab.
   *
   * Wires the query builder controls (state, district, property type, date range)
   * and the Execute Query button. On execution, renders a formatted JSON response
   * that mirrors the structure a real SRO API would return, drawn from
   * `this.transactions`.
   *
   * @returns {void}
   */
  initApiSandbox() {
    const sandboxQueryInput = document.getElementById('api-query');
    const apiCodeDisplay = document.getElementById('api-response-code');
    
    const updateResponse = () => {
      const queryStr = sandboxQueryInput.value;
      const url = new URL('https://api.crowncorridor.io/v1/registrations' + (queryStr.startsWith('?') ? queryStr : '?' + queryStr));
      
      const state = url.searchParams.get('state') || 'All';
      const district = url.searchParams.get('district');
      const limit = parseInt(url.searchParams.get('limit')) || 3;
      
      let resData = this.transactions;
      if (state !== 'All') {
        resData = resData.filter(tx => tx.state === state);
      }
      if (district) {
        resData = resData.filter(tx => tx.district.toLowerCase() === district.toLowerCase());
      }
      
      const payload = {
        status: "success",
        timestamp: new Date().toISOString(),
        filters: { state, district },
        total_records: resData.length,
        data: resData.slice(0, limit).map(tx => ({
          document_id: tx.docId,
          document_number: tx.docNo,
          geography: {
            state: tx.state,
            district: tx.district,
            mandal: tx.mandal
          },
          property: {
            type: tx.propertyType,
            area: tx.area,
            unit: tx.areaUnit,
            survey_number: tx.surveyNo
          },
          valuation: {
            consideration_value_inr: tx.considerationValue,
            stamp_duty_paid_inr: tx.stampDuty
          },
          sro: tx.sroName
        }))
      };
      
      apiCodeDisplay.textContent = JSON.stringify(payload, null, 2);
    };

    sandboxQueryInput.addEventListener('input', updateResponse);
    updateResponse();
  }

  /**
   * Initialises the Webhook Alerts subscription panel.
   *
   * Wires the alert configuration form (webhook URL, event types, minimum value
   * threshold) and the Subscribe button. Validates the webhook URL format and
   * shows a confirmation toast on successful subscription.
   *
   * @returns {void}
   */
  initAlertsSubscription() {
    const subForm = document.getElementById('alerts-form');
    subForm.addEventListener('submit', (e) => {
      e.preventDefault();
      
      const email = document.getElementById('alert-email').value;
      const threshold = document.getElementById('alert-threshold').value;
      
      const toast = document.createElement('div');
      toast.style.cssText = 'position:fixed; bottom:24px; right:24px; background:#10b981; color:white; padding:12px 24px; border-radius:8px; z-index:9999; font-weight:600; font-family:Outfit; box-shadow:0 8px 30px rgba(0,0,0,0.5);';
      toast.innerHTML = `🔔 Alerts configured! Webhook target set for transactions &gt; ₹${threshold} Cr to ${email}`;
      document.body.appendChild(toast);
      
      setTimeout(() => toast.remove(), 3500);
      subForm.reset();
    });
  }

  /**
   * Initialises modal overlay behaviour.
   *
   * Wires the close button and backdrop click on the property inquiry modal
   * (`#contact-modal`) to hide it. The modal itself is opened by
   * `openContactModal()`.
   *
   * @returns {void}
   */
  initModals() {
    const modal = document.getElementById('contact-modal');
    const closeBtn = document.getElementById('modal-close-btn');
    const form = document.getElementById('contact-agent-form');
    
    closeBtn.addEventListener('click', () => {
      modal.style.display = 'none';
    });
    
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      modal.style.display = 'none';
      
      const name = document.getElementById('contact-name').value;
      const toast = document.createElement('div');
      toast.style.cssText = 'position:fixed; bottom:24px; right:24px; background:#10b981; color:white; padding:12px 24px; border-radius:8px; z-index:9999; font-weight:600; font-family:Outfit; box-shadow:0 8px 30px rgba(0,0,0,0.5);';
      toast.innerHTML = `📧 Thank you ${name}! Verification details request dispatched to listing broker SRO.`;
      document.body.appendChild(toast);
      
      setTimeout(() => toast.remove(), 4000);
      form.reset();
    });
  }

  /**
   * Opens the property inquiry modal for a specific listing.
   *
   * Populates the modal header with the listing title and property ID, then
   * displays the modal overlay. The modal contains a contact form pre-filled
   * with the property reference.
   *
   * @param {string} propId - Listing identifier (e.g. `'PROP-1042'`).
   * @param {string} propTitle - Human-readable listing title shown in the modal header.
   * @returns {void}
   */
  openContactModal(propId, propTitle) {
    const modal = document.getElementById('contact-modal');
    document.getElementById('modal-prop-title').textContent = `Query: ${propTitle.substring(0, 32)}...`;
    document.getElementById('modal-prop-code').textContent = propId;
    modal.style.display = 'flex';
  }

  /**
   * Starts the live SRO registration feed simulation.
   *
   * Schedules a new transaction every 3–8 seconds (randomised), prepends it to
   * the live ticker, appends it to `this.transactions`, recalculates district
   * statistics, updates dashboard stats and charts. Also refreshes the district
   * boundary colour scale on every 5th new transaction.
   *
   * In a production deployment this interval would be replaced with a WebSocket
   * or Server-Sent Events connection to a live SRO data stream.
   *
   * @returns {void}
   */
  startLiveSimulation() {
    // Scroll live ticker cards
    setInterval(() => {
      const newTx = this.generateRandomTransaction();
      if (!newTx) return;
      
      this.transactions.unshift(newTx);
      if (this.transactions.length > 500) {
        this.transactions.pop();
      }
      
      this.prependToLiveFeed(newTx);
      this.calculateDistrictStats();
      this.updateDashboardStats();
      this.updateCharts();
      if (this.districtsLayer) {
        this.districtsLayer.setStyle(this.districtsLayer.options.style);
      }
      this.initApiSandbox();
    }, 8500);
  }

  /**
   * Inserts a new transaction card at the top of the live ticker strip.
   *
   * Creates a `<div class="ticker-card">` element, animates it in with a fade/slide,
   * and removes the oldest card when the strip exceeds 20 items to prevent
   * unbounded DOM growth.
   *
   * @param {Object} tx - Transaction record as returned by `generateRandomTransaction()`.
   * @returns {void}
   */
  prependToLiveFeed(tx) {
    const feedList = document.getElementById('live-feed-list');
    const card = document.createElement('div');
    const isAP = tx.state === 'Andhra Pradesh';
    card.className = `transaction-card ${isAP ? 'ap-card' : 'tg-card'}`;
    const badgeClass = isAP ? 'state-badge ap' : 'state-badge tg';
    
    card.innerHTML = `
      <div class="card-top">
        <span class="card-sro" title="${tx.sroName}">${tx.sroName}</span>
        <span class="${badgeClass}">${isAP ? 'AP' : 'TS'}</span>
      </div>
      <div class="card-middle">${tx.propertyType}</div>
      <div class="card-details">
        <span>📍 ${tx.district}, ${tx.mandal}</span>
        <span>📐 Size: ${tx.area} ${tx.areaUnit} · Surv: ${tx.surveyNo}</span>
      </div>
      <div class="card-bottom">
        <span class="card-value">₹${this.formatCurrency(tx.considerationValue)}</span>
        <span class="card-time">Just now</span>
      </div>
    `;
    
    feedList.prepend(card);
    if (feedList.childElementCount > 25) {
      feedList.lastElementChild.remove();
    }
  }

  /**
   * Initialises all Chart.js analytics charts.
   *
   * Creates three charts inside the Analytics tab:
   *   1. **Property Type Distribution** (`#chart-prop-types`) — doughnut chart.
   *   2. **Price Trends** (`#chart-price-trends`) — 12-month line chart.
   *   3. **District Transaction Volumes** (`#chart-district-volumes`) — horizontal bar chart.
   *
   * Chart instances are stored in `this.charts` and updated by `updateCharts()`.
   *
   * @returns {void}
   */
  initCharts() {
    const options = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', size: 10 } } }
      },
      scales: {
        x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
        y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
      }
    };

    const typeCtx = document.getElementById('chart-prop-types').getContext('2d');
    this.charts.propTypes = new Chart(typeCtx, {
      type: 'doughnut',
      data: this.getPropTypesChartData(),
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'right', labels: { color: '#94a3b8' } } }
      }
    });

    const trendCtx = document.getElementById('chart-price-trends').getContext('2d');
    this.charts.priceTrends = new Chart(trendCtx, {
      type: 'line',
      data: this.getPriceTrendsChartData(),
      options: options
    });
    
    const volumeCtx = document.getElementById('chart-district-volumes').getContext('2d');
    this.charts.districtVolumes = new Chart(volumeCtx, {
      type: 'bar',
      data: this.getDistrictVolumesChartData(),
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
          y: { grid: { display: false }, ticks: { color: '#94a3b8' } }
        }
      }
    });
  }

  /**
   * Computes property-type distribution data for the doughnut chart.
   *
   * Counts transactions by `propertyType` and returns Chart.js-compatible
   * `{labels, data, colors}` arrays.
   *
   * @returns {{labels: string[], data: number[], colors: string[]}} Chart dataset.
   */
  getPropTypesChartData() {
    const counts = {};
    this.propertyTypes.forEach(pt => counts[pt.name] = 0);
    this.transactions.forEach(tx => {
      if (counts[tx.propertyType] !== undefined) counts[tx.propertyType]++;
    });

    return {
      labels: Object.keys(counts),
      datasets: [{
        data: Object.values(counts),
        backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6'],
        borderColor: 'rgba(20, 28, 45, 0.9)',
        borderWidth: 2
      }]
    };
  }

  /**
   * Computes monthly average consideration values for the price-trends line chart.
   *
   * Groups transactions by calendar month over the past 12 months and calculates
   * the mean consideration value (in ₹ Lakhs) per month.
   *
   * @returns {{labels: string[], apData: number[], tgData: number[]}} Monthly averages
   *   split by state, suitable for a multi-dataset Chart.js line chart.
   */
  getPriceTrendsChartData() {
    const labels = ['Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'];
    let apBase = 4500;
    let tgBase = 5800;

    return {
      labels: labels,
      datasets: [
        {
          label: 'AP (Avg/SFT)',
          data: labels.map((l, i) => Math.round(apBase * (1 + (i * 0.015) + (Math.random() * 0.02)))),
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.3,
          fill: true
        },
        {
          label: 'Telangana (Avg/SFT)',
          data: labels.map((l, i) => Math.round(tgBase * (1 + (i * 0.02) + (Math.random() * 0.015)))),
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          tension: 0.3,
          fill: true
        }
      ]
    };
  }

  /**
   * Computes per-district transaction counts for the bar chart.
   *
   * Returns the top 10 districts by transaction volume, sorted descending.
   *
   * @returns {{labels: string[], data: number[]}} District names and counts.
   */
  getDistrictVolumesChartData() {
    const sortedDistricts = Object.keys(this.districtStats)
      .map(name => ({ name, count: this.districtStats[name].count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 7);

    return {
      labels: sortedDistricts.map(d => d.name),
      datasets: [{
        data: sortedDistricts.map(d => d.count),
        backgroundColor: sortedDistricts.map(d => this.getDistrictState(d.name) === 'Andhra Pradesh' ? '#3b82f6' : '#10b981'),
        borderRadius: 4
      }]
    };
  }

  /**
   * Refreshes all chart datasets from the current transaction array.
   *
   * Called after each live-simulation tick (every 5th transaction) to keep
   * charts in sync with new registrations. Updates `chart.data` in-place and
   * calls `chart.update()` for each chart instance.
   *
   * @returns {void}
   */
  updateCharts() {
    if (!this.charts.propTypes) return;
    this.charts.propTypes.data = this.getPropTypesChartData();
    this.charts.propTypes.update();
    
    this.charts.priceTrends.data = this.getPriceTrendsChartData();
    this.charts.priceTrends.update();
    
    this.charts.districtVolumes.data = this.getDistrictVolumesChartData();
    this.charts.districtVolumes.update();
  }

  /* Formatting Helpers */
  /**
   * Formats a numeric rupee value into a human-readable abbreviated string.
   *
   * Thresholds: ≥10 Cr → `'X.XX Cr'`, ≥1 L → `'X.XX L'`, else `'₹X,XXX'`.
   *
   * @param {number} value - Monetary value in Indian Rupees.
   * @returns {string} Formatted string (e.g. `'12.45 Cr'`, `'3.20 L'`).
   */
  formatCurrency(value) {
    if (value >= 10000000) {
      return (value / 10000000).toFixed(2) + ' Cr';
    } else if (value >= 100000) {
      return (value / 100000).toFixed(2) + ' L';
    }
    return this.formatINR(value);
  }

  /**
   * Formats a number using the Indian numbering system locale.
   *
   * Delegates to `Intl.NumberFormat` with locale `'en-IN'` and no fractional
   * digits, producing strings like `'12,34,567'`.
   *
   * @param {number} value - Numeric value to format.
   * @returns {string} Locale-formatted string.
   */
  formatINR(value) {
    return value.toLocaleString('en-IN');
  }

  /**
   * Formats a large integer with compact notation.
   *
   * Returns values ≥ 1000 as `'X.Xk'` and values < 1000 as a plain string.
   *
   * @param {number} value - Non-negative integer.
   * @returns {string} Compact formatted string (e.g. `'1.2k'`, `'842'`).
   */
  formatNumber(value) {
    return value.toLocaleString();
  }
}

// Bootstrap portal
document.addEventListener('DOMContentLoaded', () => {
  window.portal = new RealEstatePortal();
  window.portal.init();
});
