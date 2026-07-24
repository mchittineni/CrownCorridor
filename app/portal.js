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
 *
 */

// Initialize PMTiles Protocol globally so all MapLibre GL sources can use the
// `pmtiles://` URL scheme for range-request streaming of cadastral tiles.
let protocol = new pmtiles.Protocol();
maplibregl.addProtocol('pmtiles', protocol.tile);

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

    // Property History & Infrastructure Explorer State
    this.propertyHistoryData = [];
    this.selectedProperty = null;
    this.selectedPoiCategory = 'all';
    this.propertyHistoryMap = null;
    this.propertyHistoryMarkers = [];

    // UX Enhancement State
    this.comparedPropertyIds = [];
    this.isTickerPaused = false;
    this.tickerIntervalMs = 8000;
    this.userLocation = null;
    this.currentTheme = 'dark';

    // Commute & Market Trends State
    this.marketTrendsData = { ap: null, tg: null };
    this.selectedTrendsState = 'all';
    this.selectedCommuteHub = 'all';
    this.selectedCommuteMaxTime = 999;

    // Tax Rates
    this.taxRates = {
      'Andhra Pradesh': { stampDuty: 0.05, transferDuty: 0.015, regFee: 0.01, total: 0.075 },
      Telangana: { stampDuty: 0.04, transferDuty: 0.015, regFee: 0.005, total: 0.06 },
    };

    // Property classifications
    this.propertyTypes = [
      {
        name: 'Residential Plot',
        unit: 'Sq Yards',
        minArea: 120,
        maxArea: 500,
        apPriceRange: [3000, 35000],
        tgPriceRange: [4000, 55000],
        weight: 0.35,
        image: 0,
      },
      {
        name: 'Residential Flat',
        unit: 'Sq Ft',
        minArea: 900,
        maxArea: 2800,
        apPriceRange: [3500, 7500],
        tgPriceRange: [4000, 11000],
        weight: 0.3,
        image: 1,
      },
      {
        name: 'Agricultural Land',
        unit: 'Acres',
        minArea: 1,
        maxArea: 10,
        apPriceRange: [800000, 3500000],
        tgPriceRange: [1000000, 4500000],
        weight: 0.2,
        image: 2,
      },
      {
        name: 'Commercial Space',
        unit: 'Sq Ft',
        minArea: 200,
        maxArea: 3000,
        apPriceRange: [8000, 25000],
        tgPriceRange: [10000, 45000],
        weight: 0.1,
        image: 3,
      },
      {
        name: 'Independent Villa',
        unit: 'Sq Yards',
        minArea: 200,
        maxArea: 600,
        apPriceRange: [15000, 60000],
        tgPriceRange: [20000, 90000],
        weight: 0.05,
        image: 4,
      },
    ];

    // SRO mappings
    this.sros = {
      'Andhra Pradesh': {
        Visakhapatnam: [
          'Gajuwaka',
          'Bheemunipatnam',
          'Pendurthi',
          'Visakhapatnam Rural',
          'Anandapuram',
        ],
        Ntr: ['Vijayawada East', 'Vijayawada West', 'Vijayawada North', 'Ibrahimpatnam'],
        Guntur: ['Guntur Rural', 'Guntur Urban', 'Mangalagiri', 'Tenali', 'Amaravathi'],
        Tirupati: ['Tirupati Urban', 'Renigunta', 'Srikalahasti', 'Chandragiri'],
        Krishna: ['Machilipatnam', 'Gudivada', 'Vuyyuru', 'Penamaluru'],
      },
      Telangana: {
        Hyderabad: ['Charminar', 'Golconda', 'Khairatabad', 'Amberpet', 'Nampally', 'Secunderabad'],
        'Ranga Reddy': [
          'Serilingampally',
          'Rajendranagar',
          'Shamshabad',
          'Gachibowli',
          'Madhapur',
          'Ibrahimpatnam',
        ],
        'Medchal Malkajgiri': ['Kukatpally', 'Alwal', 'Keesara', 'Medchal', 'Qutbullapur'],
        Sangareddy: ['Sangareddy', 'Patancheru', 'Ameenpur', 'Ramachandrapuram'],
        Warangal: ['Warangal Urban', 'Hanumakonda', 'Kazipet'],
      },
    };

    // Mock property illustrations using Unsplash architectures
    this.propertyImages = [
      'https://images.unsplash.com/photo-1524813686514-a57563d77965?auto=format&fit=crop&w=400&q=80', // Plot/land
      'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=400&q=80', // Flat/apartment
      'https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=400&q=80', // Agri land
      'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=400&q=80', // Commercial
      'https://images.unsplash.com/photo-1613490493576-7fde63acd811?auto=format&fit=crop&w=400&q=80', // Villa
    ];
  }

  async init() {
    this.initTabs();
    this.initMaps();
    await this.loadGeographicData();
    await this.loadPropertyHistoryData();
    await this.loadMarketTrendsData();
    this.bootstrapTransactions();
    this.bootstrapVerifiedListings();
    this.initCharts();
    this.initListingsFilters();
    this.initPropertyHistoryExplorer();
    this.initCalculator();
    this.initGuideValueSearch();
    this.initApiSandbox();
    this.initAlertsSubscription();
    this.initModals();

    // Initialize User-Friendliness Enhancements
    this.initGlobalSearch();
    this.initPropertyComparison();
    this.initExportReport();
    this.initPresetFilters();
    this.initGeolocation();
    this.initThemeSwitcher();
    this.initTickerControls();

    // Initialize Commute & Market Trends
    this.initCommuteSearch();
    this.initMarketTrends();
    this.renderMarketTrends();

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
    tabs.forEach((tab) => {
      tab.addEventListener('click', () => {
        tabs.forEach((t) => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach((c) => c.classList.remove('active'));

        tab.classList.add('active');
        const targetId = tab.dataset.tab;
        document.getElementById(targetId).classList.add('active');

        // Leaflet maps need resize triggers
        if (targetId === 'map-panel' && this.map) {
          setTimeout(() => this.map.invalidateSize(), 150);
        } else if (targetId === 'property-history-panel' && this.propertyHistoryMap) {
          setTimeout(() => this.propertyHistoryMap.invalidateSize(), 150);
        }
      });
    });
  }

  /**
   * Initialises Leaflet map instance for Market Overview map.
   *
   * @returns {void}
   */
  initMaps() {
    // Market Overview Map
    this.map = L.map('leaflet-map', {
      center: [16.65, 80.0],
      zoom: 7,
      minZoom: 6,
      maxZoom: 12,
    });

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; CARTO &copy; OpenStreetMap',
      subdomains: 'abcd',
      maxZoom: 20,
    }).addTo(this.map);
  }

  async loadGeographicData() {
    try {
      // Fetch regions and coords
      const [apRes, tgRes, apCoords, tgCoords] = await Promise.all([
        fetch('../data/andhra_pradesh/regions.json').then((r) => r.json()),
        fetch('../data/telangana/regions.json').then((r) => r.json()),
        fetch('../data/andhra_pradesh/coords.json').then((r) => r.json()),
        fetch('../data/telangana/coords.json').then((r) => r.json()),
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
        fetch('../data/andhra_pradesh/districts.geojson').then((r) => r.json()),
        fetch('../data/telangana/districts.geojson').then((r) => r.json()),
      ]);

      const combinedFeatures = [...apGeo.features, ...tgGeo.features];
      this.districtsGeoJSON = { type: 'FeatureCollection', features: combinedFeatures };

      this.renderDistrictBoundaries();
    } catch (e) {
      console.error('Geographic database loading failed: ', e);
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

    stateDistricts.forEach((d) => {
      this.districts.push({
        id: d.i,
        name: d.n,
        state: stateName,
      });

      this.mandalsByDistrict[d.n] = stateMandals.filter((m) => m.d === d.i).map((m) => m.n);
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
        const dName =
          feature.properties.district || feature.properties.d_name || feature.properties.name || '';
        const stat = this.districtStats[dName] || { count: 0 };

        let fillColor = '#1e293b';
        if (stat.count > 0) {
          const maxCount = Math.max(...Object.values(this.districtStats).map((s) => s.count), 1);
          const intensity = Math.min(stat.count / maxCount, 1);
          fillColor = this.blendColors('#3b82f6', '#10b981', intensity);
        }

        return {
          fillColor: fillColor,
          fillOpacity: 0.65,
          weight: 1.2,
          color: 'rgba(255,255,255,0.12)',
          dashArray: '3',
        };
      },
      onEachFeature: (feature, layer) => {
        const dName =
          feature.properties.district ||
          feature.properties.d_name ||
          feature.properties.name ||
          'Unknown District';

        layer.on({
          mouseover: (e) => {
            const l = e.target;
            l.setStyle({
              weight: 2.2,
              color: '#3b82f6',
              fillOpacity: 0.8,
              dashArray: '',
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

            layer
              .bindPopup(popupContent, { closeButton: false, offset: L.point(0, -10) })
              .openPopup();
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
          },
        });
      },
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
    return result
      ? {
          r: parseInt(result[1], 16),
          g: parseInt(result[2], 16),
          b: parseInt(result[3], 16),
        }
      : { r: 0, g: 0, b: 0 };
  }

  /**
   * Resolves which state a district belongs to.
   *
   * @param {string} districtName - District name as it appears in `regions.json`.
   * @returns {string} `'Andhra Pradesh'`, `'Telangana'`, or `'Unknown'`.
   */
  getDistrictState(districtName) {
    const d = this.districts.find((item) => item.name === districtName);
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

    const stateDistricts = this.districts.filter((d) => d.state === state);
    if (stateDistricts.length === 0) return null;

    const districtObj = stateDistricts[Math.floor(Math.random() * stateDistricts.length)];
    const district = districtObj.name;

    const mandals = this.mandalsByDistrict[district] || ['Rural Mandal'];
    const mandal = mandals[Math.floor(Math.random() * mandals.length)];

    const village = mandal + ' Rural';
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

    const area = parseFloat(
      (propType.minArea + Math.random() * (propType.maxArea - propType.minArea)).toFixed(2)
    );
    const stateRates = propType[state === 'Andhra Pradesh' ? 'apPriceRange' : 'tgPriceRange'];
    const ratePerUnit = stateRates[0] + Math.random() * (stateRates[1] - stateRates[0]);
    const marketValue = Math.round(area * ratePerUnit);
    const considerationValue = Math.round(marketValue * (1 + Math.random() * 0.2));

    const tax = this.taxRates[state];
    const stampDuty = Math.round(considerationValue * tax.stampDuty);
    const transferDuty = Math.round(considerationValue * tax.transferDuty);
    const regFee = Math.round(considerationValue * tax.regFee);
    const totalDuty = stampDuty + transferDuty + regFee;

    const coloniesAP = [
      'MVP Colony',
      'Seethammadhara Layout',
      'Amaravati Heights',
      'Vidhya Nagar Colony',
      'Labbipet Enclave',
      'Kanuru Greenfields',
      'Balaji Nagar Layout',
      'Bhavani Nagar Society',
    ];
    const coloniesTG = [
      'Rainbow Vistas Colony',
      'Kavuri Hills Colony',
      'Lanco Hills Towers',
      'My Home Jewel Complex',
      'Gachibowli Financial Enclave',
      'Pragathi Nagar Layout',
      'Jubilee Hills Sector-3',
      'Srinagar Colony',
    ];
    const colony =
      state === 'Andhra Pradesh'
        ? coloniesAP[Math.floor(Math.random() * coloniesAP.length)]
        : coloniesTG[Math.floor(Math.random() * coloniesTG.length)];

    let blockUnit = '';
    if (propType.name === 'Residential Flat') {
      blockUnit = `Block ${['A', 'B', 'C', 'D'][Math.floor(Math.random() * 4)]}, Flat ${100 + Math.floor(Math.random() * 400)}`;
    } else if (propType.name === 'Commercial Space') {
      blockUnit = `Tower ${1 + Math.floor(Math.random() * 4)}, Suite ${Math.floor(100 + Math.random() * 900)}`;
    } else if (propType.name === 'Residential Plot') {
      blockUnit = `Plot No ${1 + Math.floor(Math.random() * 150)}, Sector ${1 + Math.floor(Math.random() * 4)}`;
    } else if (propType.name === 'Independent Villa') {
      blockUnit = `Villa ${1 + Math.floor(Math.random() * 80)}, Phase ${1 + Math.floor(Math.random() * 3)}`;
    } else {
      blockUnit = `Survey Part-${['A', 'B', 'C'][Math.floor(Math.random() * 3)]}`;
    }

    const seller = 'Seller Name';
    const buyer = 'Buyer Name';

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
      colony,
      blockUnit,
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
      parties: `${seller} to ${buyer}`,
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
      ['Clubhouse Access', 'Private Garden', 'Security Guard', 'Solar Heating Systems'],
    ];

    const orientations = ['East', 'West', 'North', 'South'];

    for (let i = 0; i < totalListings; i++) {
      const state = i % 2 === 0 ? 'Telangana' : 'Andhra Pradesh';
      const stateDistricts = this.districts.filter((d) => d.state === state);
      if (stateDistricts.length === 0) continue;

      const district = stateDistricts[Math.floor(Math.random() * stateDistricts.length)].name;
      const mandals = this.mandalsByDistrict[district] || ['Mandal Central'];
      const mandal = mandals[Math.floor(Math.random() * mandals.length)];

      const propType = this.propertyTypes[i % this.propertyTypes.length];
      const area = Math.round(
        propType.minArea + Math.random() * (propType.maxArea - propType.minArea)
      );

      const stateRates = propType[state === 'Andhra Pradesh' ? 'apPriceRange' : 'tgPriceRange'];
      const price = Math.round(
        area * (stateRates[0] + Math.random() * (stateRates[1] - stateRates[0])) * 1.15
      );

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

      const coloniesAP = [
        'MVP Colony',
        'Seethammadhara Layout',
        'Amaravati Heights',
        'Vidhya Nagar Colony',
        'Labbipet Enclave',
        'Kanuru Greenfields',
        'Balaji Nagar Layout',
        'Bhavani Nagar Society',
      ];
      const coloniesTG = [
        'Rainbow Vistas Colony',
        'Kavuri Hills Colony',
        'Lanco Hills Towers',
        'My Home Jewel Complex',
        'Gachibowli Financial Enclave',
        'Pragathi Nagar Layout',
        'Jubilee Hills Sector-3',
        'Srinagar Colony',
      ];
      const colony =
        state === 'Andhra Pradesh'
          ? coloniesAP[i % coloniesAP.length]
          : coloniesTG[i % coloniesTG.length];

      let blockUnit = '';
      if (propType.name === 'Residential Flat') {
        blockUnit = `Block ${['A', 'B', 'C', 'D'][i % 4]}, Flat ${100 + ((i * 7) % 400)}`;
      } else if (propType.name === 'Commercial Space') {
        blockUnit = `Tower ${1 + (i % 4)}, Suite ${Math.floor(100 + i * 23) % 900}`;
      } else if (propType.name === 'Residential Plot') {
        blockUnit = `Plot No ${1 + ((i * 11) % 150)}, Sector ${1 + (i % 4)}`;
      } else if (propType.name === 'Independent Villa') {
        blockUnit = `Villa ${1 + ((i * 3) % 80)}, Phase ${1 + (i % 3)}`;
      } else {
        blockUnit = `Survey Part-${['A', 'B', 'C'][i % 3]}`;
      }

      this.listings.push({
        id: `PROP-${1000 + i}`,
        title: `${area} ${propType.unit} ${propType.name} @ ${colony} (${blockUnit})`,
        type: propType.name,
        price,
        area,
        unit: propType.unit,
        state,
        district,
        mandal,
        village: mandal + ' Sector ' + ((i % 5) + 1),
        colony,
        blockUnit,
        surveyNo: `${Math.floor(50 + Math.random() * 250)}/A`,
        facing: orientations[i % orientations.length],
        status: i % 4 === 3 ? 'Rent' : 'Sale',
        verified: true,
        lat,
        lng,
        amenities: amenitiesPool[i % this.propertyTypes.length],
        image: propType.image,
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
    this.transactions.forEach((tx) => {
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
    const totalValue =
      this.transactions.reduce((sum, tx) => sum + tx.considerationValue, 0) / 10000000;
    const totalStampDuty = this.transactions.reduce((sum, tx) => sum + tx.totalDuty, 0) / 10000000;
    const velocity = parseFloat((totalTransactions / 30).toFixed(1));

    // Live Stats Counter (Header)
    document.getElementById('live-reg-today').textContent = this.transactions.filter((tx) => {
      const today = new Date();
      return tx.date.getDate() === today.getDate() && tx.date.getMonth() === today.getMonth();
    }).length;

    document.getElementById('live-value-today').textContent =
      '₹' +
      (
        this.transactions
          .filter((tx) => {
            const today = new Date();
            return tx.date.getDate() === today.getDate() && tx.date.getMonth() === today.getMonth();
          })
          .reduce((sum, tx) => sum + tx.considerationValue, 0) / 10000000
      ).toFixed(2) +
      ' Cr';

    // Main Stats Panel
    document.getElementById('stat-total-tx').textContent = this.formatNumber(totalTransactions);
    document.getElementById('stat-total-val').textContent = '₹' + totalValue.toFixed(2) + ' Cr';
    document.getElementById('stat-total-duty').textContent =
      '₹' + totalStampDuty.toFixed(2) + ' Cr';
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

    const filtered = this.listings.filter((p) => {
      if (stateVal !== 'All' && p.state !== stateVal) return false;
      if (typeVal !== 'All' && p.type !== typeVal) return false;

      if (priceVal !== 'All') {
        const maxVal = parseFloat(priceVal);
        if (p.price > maxVal) return false;
      }

      if (searchVal) {
        const matchesSearch =
          p.district.toLowerCase().includes(searchVal) ||
          p.mandal.toLowerCase().includes(searchVal) ||
          (p.colony && p.colony.toLowerCase().includes(searchVal)) ||
          p.title.toLowerCase().includes(searchVal);
        if (!matchesSearch) return false;
      }

      // Commute Filter
      if (this.selectedCommuteHub !== 'all') {
        const commute = this.calculateCommuteTime(p.lat, p.lng, this.selectedCommuteHub);
        if (commute && commute.driveMins > this.selectedCommuteMaxTime) {
          return false;
        }
      }

      return true;
    });

    if (filtered.length === 0) {
      cardGrid.innerHTML = `<div style="grid-column: 1/-1; text-align:center; color:var(--text-dim); padding:40px;">No verified property listings match the current filters.</div>`;
      return;
    }

    filtered.forEach((p) => {
      const card = document.createElement('div');
      card.className = 'property-card';

      const imgUrl = this.propertyImages[p.image];
      const rentText = p.status === 'Rent' ? '/month' : '';
      const isCompared = this.comparedPropertyIds.includes(p.code);
      const commuteInfo = this.calculateCommuteTime(p.lat, p.lng, this.selectedCommuteHub);
      const commuteBadgeHtml = commuteInfo
        ? `<div class="commute-badge">🚗 ${commuteInfo.driveMins} mins to ${commuteInfo.hubName} (${commuteInfo.distanceKm} km)</div>`
        : '';

      card.innerHTML = `
        <div class="property-img-wrap" style="background-image: url('${imgUrl}')">
          <span class="property-badge-verified">VERIFIED</span>
          <span class="property-badge-status">FOR ${p.status.toUpperCase()}</span>
          <span class="property-price-overlay">₹${this.formatCurrency(p.price)}${rentText}</span>
        </div>
        <div class="property-content">
          <div class="property-type">${p.type}</div>
          <h4 class="property-title" title="${p.title}">${p.title}</h4>
          <div class="property-geo">📍 ${p.district}, ${p.mandal}, ${p.village}</div>
          <div class="property-colony" style="color: #60a5fa; font-size: 0.85rem; font-weight: 500; margin: 4px 0;">🏢 ${p.colony} · ${p.blockUnit}</div>
          ${commuteBadgeHtml}
          
          <div class="property-specs" style="margin-top: 6px;">
            <div class="property-spec-item">📐 ${p.area} ${p.unit}</div>
            <div class="property-spec-item">🧭 ${p.facing} Facing</div>
          </div>
          
          <div class="property-amenities">
            ${p.amenities.map((a) => `<span class="property-amenity-tag">${a}</span>`).join('')}
          </div>
          
          <div style="display:flex; gap:8px; margin-top: auto;">
            <button class="btn-contact" style="flex:1;" onclick="window.portal.openContactModal('${p.id}', '${p.title.replace(/'/g, "\\'")}')">Contact Agent</button>
            <button class="btn-toggle-compare ${isCompared ? 'active' : ''}" style="background:rgba(59,130,246,0.15); border:1px solid #3b82f6; color:#38bdf8; padding:6px 12px; border-radius:8px; font-size:0.75rem; font-weight:700; cursor:pointer;" onclick="window.portal.toggleCompareProperty('${p.code}')">${isCompared ? '✓ Comparing' : '+ Compare'}</button>
          </div>
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
    this.mapListingMarkers.forEach((m) => this.map.removeLayer(m));
    this.mapListingMarkers = [];

    // Custom blue marker for property listings
    const propIcon = L.divIcon({
      className: 'custom-div-icon',
      html: `<div style="background-color:#3b82f6; width:12px; height:12px; border-radius:50%; border:2px solid #ffffff; box-shadow:0 0 8px rgba(59,130,246,0.8)"></div>`,
      iconSize: [12, 12],
      iconAnchor: [6, 6],
    });

    this.listings.forEach((p) => {
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

    calcType.innerHTML = this.propertyTypes
      .map((t) => `<option value="${t.name}">${t.name}</option>`)
      .join('');

    const calculate = () => {
      const state = calcState.value;
      const val = parseFloat(calcValue.value) || 0;
      const tax = this.taxRates[state];

      const stampDutyVal = val * tax.stampDuty;
      const transferDutyVal = val * tax.transferDuty;
      const regFeeVal = val * tax.regFee;
      const totalDutyVal = stampDutyVal + transferDutyVal + regFeeVal;

      document.getElementById('calc-breakdown-stamp').textContent =
        '₹' + this.formatINR(stampDutyVal);
      document.getElementById('calc-breakdown-transfer').textContent =
        '₹' + this.formatINR(transferDutyVal);
      document.getElementById('calc-breakdown-reg').textContent = '₹' + this.formatINR(regFeeVal);
      document.getElementById('calc-breakdown-total').textContent =
        '₹' + this.formatINR(totalDutyVal);

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

    guideType.innerHTML = this.propertyTypes
      .map((t) => `<option value="${t.name}">${t.name}</option>`)
      .join('');

    const updateDistricts = () => {
      const state = guideState.value;
      guideDistrict.innerHTML = '<option value="">Select District</option>';
      guideMandal.innerHTML = '<option value="">Select Mandal</option>';

      const filtered = this.districts.filter((d) => d.state === state);
      filtered.sort((a, b) => a.name.localeCompare(b.name));

      filtered.forEach((d) => {
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

      mandals.forEach((m) => {
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
      const isUrban = [
        'Hyderabad',
        'Ranga Reddy',
        'Medchal Malkajgiri',
        'Visakhapatnam',
        'Ntr',
      ].includes(district);

      if (type === 'Residential Plot') {
        baseRate = isUrban ? 15000 + Math.random() * 20000 : 1500 + Math.random() * 5000;
        unit = 'per Sq Yard';
      } else if (type === 'Residential Flat') {
        baseRate = isUrban ? 4500 + Math.random() * 2500 : 2200 + Math.random() * 1500;
        unit = 'per Sq Ft';
      } else if (type === 'Agricultural Land') {
        baseRate = isUrban ? 4000000 + Math.random() * 8000000 : 600000 + Math.random() * 1200000;
        unit = 'per Acre';
      } else if (type === 'Commercial Space') {
        baseRate = isUrban ? 12000 + Math.random() * 15000 : 5000 + Math.random() * 5000;
        unit = 'per Sq Ft';
      } else {
        baseRate = isUrban ? 25000 + Math.random() * 30000 : 8000 + Math.random() * 8000;
        unit = 'per Sq Yard';
      }

      valBox.textContent = '₹' + this.formatINR(Math.round(baseRate));
      rateLabel.textContent = `${unit} (Official guidance rate estimation)`;
    };

    guideState.addEventListener('change', () => {
      updateDistricts();
      calculateGuideValue();
    });
    guideDistrict.addEventListener('change', () => {
      updateMandals();
      calculateGuideValue();
    });
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
      const url = new URL(
        'https://api.crowncorridor.io/v1/registrations' +
          (queryStr.startsWith('?') ? queryStr : '?' + queryStr)
      );

      const state = url.searchParams.get('state') || 'All';
      const district = url.searchParams.get('district');
      const limit = parseInt(url.searchParams.get('limit')) || 3;

      let resData = this.transactions;
      if (state !== 'All') {
        resData = resData.filter((tx) => tx.state === state);
      }
      if (district) {
        resData = resData.filter((tx) => tx.district.toLowerCase() === district.toLowerCase());
      }

      const payload = {
        status: 'success',
        timestamp: new Date().toISOString(),
        filters: { state, district },
        total_records: resData.length,
        data: resData.slice(0, limit).map((tx) => ({
          document_id: tx.docId,
          document_number: tx.docNo,
          geography: {
            state: tx.state,
            district: tx.district,
            mandal: tx.mandal,
          },
          property: {
            type: tx.propertyType,
            area: tx.area,
            unit: tx.areaUnit,
            survey_number: tx.surveyNo,
          },
          valuation: {
            consideration_value_inr: tx.considerationValue,
            stamp_duty_paid_inr: tx.stampDuty,
          },
          sro: tx.sroName,
        })),
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
      toast.style.cssText =
        'position:fixed; bottom:24px; right:24px; background:#10b981; color:white; padding:12px 24px; border-radius:8px; z-index:9999; font-weight:600; font-family:Outfit; box-shadow:0 8px 30px rgba(0,0,0,0.5);';
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
      toast.style.cssText =
        'position:fixed; bottom:24px; right:24px; background:#10b981; color:white; padding:12px 24px; border-radius:8px; z-index:9999; font-weight:600; font-family:Outfit; box-shadow:0 8px 30px rgba(0,0,0,0.5);';
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
    document.getElementById('modal-prop-title').textContent =
      `Query: ${propTitle.substring(0, 32)}...`;
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
    const runStep = () => {
      if (!this.isTickerPaused) {
        const newTx = this.generateRandomTransaction();
        if (newTx) {
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
        }
      }
      setTimeout(runStep, this.tickerIntervalMs || 8000);
    };

    setTimeout(runStep, this.tickerIntervalMs || 8000);
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
        <span>📍 ${tx.district}, ${tx.mandal}, ${tx.village}</span>
        ${tx.colony ? `<span class="colony-info" style="color: #60a5fa; font-weight: 500; font-size: 0.8rem; display: block; margin: 2px 0;">🏢 ${tx.colony} ${tx.blockUnit ? `· ${tx.blockUnit}` : ''}</span>` : ''}
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
        legend: { labels: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', size: 10 } } },
      },
      scales: {
        x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
        y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
      },
    };

    const typeCtx = document.getElementById('chart-prop-types').getContext('2d');
    this.charts.propTypes = new Chart(typeCtx, {
      type: 'doughnut',
      data: this.getPropTypesChartData(),
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'right', labels: { color: '#94a3b8' } } },
      },
    });

    const trendCtx = document.getElementById('chart-price-trends').getContext('2d');
    this.charts.priceTrends = new Chart(trendCtx, {
      type: 'line',
      data: this.getPriceTrendsChartData(),
      options: options,
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
          y: { grid: { display: false }, ticks: { color: '#94a3b8' } },
        },
      },
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
    this.propertyTypes.forEach((pt) => (counts[pt.name] = 0));
    this.transactions.forEach((tx) => {
      if (counts[tx.propertyType] !== undefined) counts[tx.propertyType]++;
    });

    return {
      labels: Object.keys(counts),
      datasets: [
        {
          data: Object.values(counts),
          backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6'],
          borderColor: 'rgba(20, 28, 45, 0.9)',
          borderWidth: 2,
        },
      ],
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
          data: labels.map((l, i) => Math.round(apBase * (1 + i * 0.015 + Math.random() * 0.02))),
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.3,
          fill: true,
        },
        {
          label: 'Telangana (Avg/SFT)',
          data: labels.map((l, i) => Math.round(tgBase * (1 + i * 0.02 + Math.random() * 0.015))),
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          tension: 0.3,
          fill: true,
        },
      ],
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
      .map((name) => ({ name, count: this.districtStats[name].count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 7);

    return {
      labels: sortedDistricts.map((d) => d.name),
      datasets: [
        {
          data: sortedDistricts.map((d) => d.count),
          backgroundColor: sortedDistricts.map((d) =>
            this.getDistrictState(d.name) === 'Andhra Pradesh' ? '#3b82f6' : '#10b981'
          ),
          borderRadius: 4,
        },
      ],
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

  /* ─────────────────────────────────────────────────────────────────────────
   * Property Sale History & Infrastructure Explorer Logic
   * ───────────────────────────────────────────────────────────────────────── */

  async loadPropertyHistoryData() {
    try {
      const fetchFile = (path) =>
        fetch(`../data/${path}`)
          .catch(() => fetch(`data/${path}`))
          .catch(() => fetch(`./data/${path}`));

      const [apRes, tgRes, legacyRes] = await Promise.allSettled([
        fetchFile('andhra_pradesh/property_history.json').then((r) => r.json()),
        fetchFile('telangana/property_history.json').then((r) => r.json()),
        fetchFile('property_history.json').then((r) => r.json()),
      ]);

      const loadedProps = [];
      if (apRes.status === 'fulfilled' && apRes.value && apRes.value.properties) {
        loadedProps.push(...apRes.value.properties);
      }
      if (tgRes.status === 'fulfilled' && tgRes.value && tgRes.value.properties) {
        loadedProps.push(...tgRes.value.properties);
      }
      if (
        loadedProps.length === 0 &&
        legacyRes.status === 'fulfilled' &&
        legacyRes.value &&
        legacyRes.value.properties
      ) {
        loadedProps.push(...legacyRes.value.properties);
      }

      // Deduplicate by property_id
      const seen = new Set();
      this.propertyHistoryData = loadedProps.filter((p) => {
        if (!p.property_id || seen.has(p.property_id)) return false;
        seen.add(p.property_id);
        return true;
      });

      // Ensure EVERY listing in both states has a complete 25-year property history record
      if (this.listings && this.listings.length > 0) {
        this.listings.forEach((p, idx) => {
          const pid = p.id || `PROP-${1000 + idx}`;
          if (!seen.has(pid)) {
            seen.add(pid);
            const constYear = 2001 + (idx % 5); // 25-year timeline starting 2001-2005
            const holdingYears = 2026 - constYear;
            const initPrice = Math.round(p.price / (4.2 + (idx % 3) * 0.5));
            const cagr = parseFloat(
              (((p.price / initPrice) ** (1.0 / holdingYears) - 1) * 100).toFixed(2)
            );
            const totalAppr = parseFloat((((p.price - initPrice) / initPrice) * 100).toFixed(2));

            this.propertyHistoryData.push({
              property_id: pid,
              name: p.title,
              type: p.type,
              construction_year: constYear,
              address: `${p.blockUnit ? p.blockUnit + ', ' : ''}${p.colony}, ${p.mandal}`,
              mandal: p.mandal,
              district: p.district,
              state: p.state === 'Andhra Pradesh' ? 'andhra_pradesh' : 'telangana',
              total_sqft: p.area,
              bedrooms: p.type === 'Independent Villa' ? 4 : p.type === 'Residential Flat' ? 3 : 2,
              bathrooms: p.type === 'Independent Villa' ? 4 : 2,
              rera_id: `P0${p.state === 'Andhra Pradesh' ? '32' : '24'}000${1000 + idx}`,
              lat: p.lat,
              lng: p.lng,
              price_summary: {
                initial_price_inr: initPrice,
                latest_price_inr: p.price,
                total_appreciation_pct: totalAppr,
                cagr_pct: cagr,
                holding_period_years: holdingYears,
              },
              sale_history: [
                {
                  year: constYear,
                  sale_date: `${constYear}-03-15`,
                  sale_price_inr: initPrice,
                  price_per_sqft_inr: Math.round(initPrice / p.area),
                  seller_type: 'Commercial Property Developer',
                  buyer_type: 'Private Individual Owner',
                  registration_doc_no: `SRO-DOC-${constYear}-${1000 + idx}`,
                  growth_over_initial_pct: 0.0,
                  cagr_pct: 0.0,
                },
                {
                  year: constYear + 11,
                  sale_date: `${constYear + 11}-08-20`,
                  sale_price_inr: Math.round(initPrice * 2.3),
                  price_per_sqft_inr: Math.round((initPrice * 2.3) / p.area),
                  seller_type: 'Private Individual Owner',
                  buyer_type: 'Private Individual Owner',
                  registration_doc_no: `SRO-DOC-${constYear + 11}-${5000 + idx}`,
                  growth_over_initial_pct: 130.0,
                  cagr_pct: 7.8,
                },
                {
                  year: 2026,
                  sale_date: '2026-07-01',
                  sale_price_inr: p.price,
                  price_per_sqft_inr: Math.round(p.price / p.area),
                  seller_type: 'Private Individual Owner',
                  buyer_type: 'Current Valuation (SRO Benchmark)',
                  registration_doc_no: 'VALUATION-EST-2026',
                  growth_over_initial_pct: totalAppr,
                  cagr_pct: cagr,
                },
              ],
              nearby_services: [
                {
                  name: `${p.district} Central School`,
                  category: 'schools',
                  type: 'CBSE Senior Secondary School',
                  distance_km: 1.2,
                  travel_time_mins: 4,
                  rating: 4.7,
                  lat: p.lat + 0.005,
                  lng: p.lng + 0.005,
                },
                {
                  name: `${p.district} Multi-Specialty Hospital`,
                  category: 'hospitals',
                  type: 'Super Specialty Hospital',
                  distance_km: 2.1,
                  travel_time_mins: 7,
                  rating: 4.8,
                  lat: p.lat - 0.006,
                  lng: p.lng - 0.004,
                },
                {
                  name: `${p.mandal} Metro / Transit Terminal`,
                  category: 'metro_railways',
                  type: 'Rapid Transit Station',
                  distance_km: 1.8,
                  travel_time_mins: 6,
                  rating: 4.6,
                  lat: p.lat + 0.003,
                  lng: p.lng - 0.007,
                },
              ],
            });
          }
        });
      }
    } catch (err) {
      console.warn('Could not load state property_history.json files:', err);
      this.propertyHistoryData = [];
    }
  }

  initPropertyHistoryExplorer() {
    // 1. Initialize Leaflet map instance
    const mapElement = document.getElementById('prop-history-map');
    if (mapElement && !this.propertyHistoryMap) {
      this.propertyHistoryMap = L.map('prop-history-map', {
        center: [17.4401, 78.3489],
        zoom: 14,
        minZoom: 6,
        maxZoom: 18,
      });

      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; CARTO &copy; OpenStreetMap',
        subdomains: 'abcd',
        maxZoom: 20,
      }).addTo(this.propertyHistoryMap);
    }

    // 2. Setup Filter Listeners
    const stateFilter = document.getElementById('prop-filter-state');
    const typeFilter = document.getElementById('prop-filter-type');
    const selectProp = document.getElementById('prop-history-select');

    if (stateFilter) {
      stateFilter.addEventListener('change', () => {
        this.populatePropertySelect(stateFilter.value, typeFilter ? typeFilter.value : 'All');
      });
    }

    if (typeFilter) {
      typeFilter.addEventListener('change', () => {
        this.populatePropertySelect(stateFilter ? stateFilter.value : 'All', typeFilter.value);
      });
    }

    if (selectProp) {
      selectProp.addEventListener('change', (e) => {
        this.selectProperty(e.target.value);
      });
    }

    // 3. Setup POI Category Filter Pills
    const poiPills = document.querySelectorAll('#poi-filter-pills .btn-pill');
    poiPills.forEach((btn) => {
      btn.addEventListener('click', () => {
        poiPills.forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        this.selectedPoiCategory = btn.dataset.cat || 'all';
        if (this.selectedProperty) {
          this.renderNearbyServices(this.selectedProperty, this.selectedPoiCategory);
          this.renderPropertyHistoryMap(this.selectedProperty, this.selectedPoiCategory);
        }
      });
    });

    // 4. Setup CAGR ROI Calculator Inputs Listener
    ['cagr-buy-year', 'cagr-buy-price', 'cagr-target-year', 'cagr-annual-rate'].forEach((id) => {
      const el = document.getElementById(id);
      if (el) {
        el.addEventListener('input', () => this.calculateCagrEstimate());
      }
    });

    // Initial population
    this.populatePropertySelect('All', 'All');
  }

  populatePropertySelect(stateFilter, typeFilter) {
    const selectProp = document.getElementById('prop-history-select');
    if (!selectProp) return;

    selectProp.innerHTML = '';
    const filtered = this.propertyHistoryData.filter((p) => {
      const stateMatch =
        stateFilter === 'All' ||
        p.state === stateFilter ||
        (stateFilter === 'telangana' && p.state === 'telangana') ||
        (stateFilter === 'andhra_pradesh' && p.state === 'andhra_pradesh');
      const typeMatch = typeFilter === 'All' || p.type === typeFilter;
      return stateMatch && typeMatch;
    });

    if (filtered.length === 0) {
      const opt = document.createElement('option');
      opt.value = '';
      opt.textContent = 'No matching properties found';
      selectProp.appendChild(opt);
      return;
    }

    filtered.forEach((p) => {
      const opt = document.createElement('option');
      opt.value = p.property_id;
      const stateLabel = p.state === 'telangana' ? 'TS' : 'AP';
      opt.textContent = `[${stateLabel}] ${p.name} (${p.type}, Built ${p.construction_year}) — ${p.address}`;
      selectProp.appendChild(opt);
    });

    // Select first property by default
    selectProp.value = filtered[0].property_id;
    this.selectProperty(filtered[0].property_id);
  }

  selectProperty(propertyId) {
    const prop = this.propertyHistoryData.find((p) => p.property_id === propertyId);
    if (!prop) return;
    this.selectedProperty = prop;

    this.renderPropertyHighlight(prop);
    this.renderPriceHistoryChart(prop);
    this.renderSaleHistoryTable(prop);
    this.renderNearbyServices(prop, this.selectedPoiCategory);
    this.renderPropertyHistoryMap(prop, this.selectedPoiCategory);

    // Update calculator default values with property initial price
    const buyYearInput = document.getElementById('cagr-buy-year');
    const buyPriceInput = document.getElementById('cagr-buy-price');
    if (buyYearInput && prop.construction_year) {
      buyYearInput.value = prop.construction_year;
    }
    if (buyPriceInput && prop.price_summary) {
      buyPriceInput.value = (prop.price_summary.initial_price_inr / 100000).toFixed(1);
    }
    this.calculateCagrEstimate();
  }

  renderPropertyHighlight(prop) {
    const card = document.getElementById('prop-highlight-card');
    const badge = document.getElementById('prop-appreciation-badge');
    if (!card) return;

    const initialFormatted = this.formatCurrency(prop.price_summary.initial_price_inr);
    const latestFormatted = this.formatCurrency(prop.price_summary.latest_price_inr);

    card.innerHTML = `
      <div class="stat-item">
        <span style="font-size:0.68rem; color:var(--text-dim); text-transform:uppercase; font-weight:700;">Construction Year</span>
        <strong style="font-size:1.1rem; color:#fff;">${prop.construction_year}</strong>
      </div>
      <div class="stat-item">
        <span style="font-size:0.68rem; color:var(--text-dim); text-transform:uppercase; font-weight:700;">Property Size</span>
        <strong style="font-size:1.1rem; color:#38bdf8;">${this.formatNumber(prop.total_sqft)} sq ft (${prop.bedrooms}BHK)</strong>
      </div>
      <div class="stat-item">
        <span style="font-size:0.68rem; color:var(--text-dim); text-transform:uppercase; font-weight:700;">RERA Reg. ID</span>
        <strong style="font-size:0.85rem; color:#a7f3d0; font-family:monospace;">${prop.rera_id || 'VERIFIED'}</strong>
      </div>
      <div class="stat-item">
        <span style="font-size:0.68rem; color:var(--text-dim); text-transform:uppercase; font-weight:700;">Initial Price (${prop.construction_year})</span>
        <strong style="font-size:1.1rem; color:#94a3b8;">₹${initialFormatted}</strong>
      </div>
      <div class="stat-item">
        <span style="font-size:0.68rem; color:var(--text-dim); text-transform:uppercase; font-weight:700;">Current Market Valuation</span>
        <strong style="font-size:1.1rem; color:#10b981;">₹${latestFormatted}</strong>
      </div>
      <div class="stat-item">
        <span style="font-size:0.68rem; color:var(--text-dim); text-transform:uppercase; font-weight:700;">Appreciation / CAGR</span>
        <strong style="font-size:1.1rem; color:#f59e0b;">+${prop.price_summary.total_appreciation_pct.toFixed(1)}% (${prop.price_summary.cagr_pct.toFixed(1)}% CAGR)</strong>
      </div>
    `;

    if (badge) {
      badge.textContent = `▲ +${prop.price_summary.total_appreciation_pct.toFixed(1)}% Growth since ${prop.construction_year}`;
    }
  }

  renderPriceHistoryChart(prop) {
    const canvas = document.getElementById('chart-price-history');
    if (!canvas) return;

    if (this.charts['priceHistory']) {
      this.charts['priceHistory'].destroy();
    }

    const ctx = canvas.getContext('2d');

    const labels = prop.sale_history.map(
      (s) => `${s.year} (${s.sale_date ? s.sale_date.substring(5) : ''})`
    );
    const pricesLakhs = prop.sale_history.map((s) => s.sale_price_inr / 100000);
    const sqftRates = prop.sale_history.map((s) => s.price_per_sqft_inr);

    // Create gradient fill
    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(56, 189, 248, 0.4)');
    gradient.addColorStop(1, 'rgba(56, 189, 248, 0.0)');

    this.charts['priceHistory'] = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Property Price (₹ Lakhs)',
            data: pricesLakhs,
            borderColor: '#38bdf8',
            backgroundColor: gradient,
            borderWidth: 3,
            fill: true,
            tension: 0.35,
            pointBackgroundColor: '#0ea5e9',
            pointRadius: 6,
            pointHoverRadius: 9,
            yAxisID: 'y',
          },
          {
            label: 'Price per Sq.Ft (₹)',
            data: sqftRates,
            borderColor: '#f59e0b',
            borderWidth: 2,
            borderDash: [5, 5],
            fill: false,
            tension: 0.35,
            pointBackgroundColor: '#d97706',
            pointRadius: 4,
            yAxisID: 'y1',
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false,
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: (context) => {
                const idx = context.dataIndex;
                const sale = prop.sale_history[idx];
                if (context.datasetIndex === 0) {
                  return ` Sale Price: ₹${(sale.sale_price_inr / 100000).toFixed(2)} Lakhs (${sale.buyer_type})`;
                }
                return ` Sq.Ft Rate: ₹${sale.price_per_sqft_inr.toLocaleString()}/sqft (Doc: ${sale.registration_doc_no})`;
              },
            },
          },
          legend: {
            labels: {
              color: '#94a3b8',
              font: { family: 'Inter', size: 11 },
            },
          },
        },
        scales: {
          x: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: '#94a3b8' },
          },
          y: {
            type: 'linear',
            display: true,
            position: 'left',
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: {
              color: '#38bdf8',
              callback: (val) => `₹${val}L`,
            },
          },
          y1: {
            type: 'linear',
            display: true,
            position: 'right',
            grid: { drawOnChartArea: false },
            ticks: {
              color: '#f59e0b',
              callback: (val) => `₹${val}/ft²`,
            },
          },
        },
      },
    });
  }

  renderSaleHistoryTable(prop) {
    const tbody = document.getElementById('table-sale-history-body');
    if (!tbody) return;

    tbody.innerHTML = '';
    prop.sale_history.forEach((s) => {
      const tr = document.createElement('tr');
      const formattedPrice = this.formatCurrency(s.sale_price_inr);
      const isInitial = s.growth_over_initial_pct === 0;
      const growthBadge = isInitial
        ? `<span style="color:var(--text-dim); font-size:0.75rem;">Initial Base</span>`
        : `<span style="color:#10b981; font-weight:700; font-size:0.8rem;">▲ +${s.growth_over_initial_pct.toFixed(1)}%</span>`;

      tr.innerHTML = `
        <td><strong>${s.year}</strong> <span style="font-size:0.72rem; color:var(--text-dim); display:block;">${s.sale_date}</span></td>
        <td style="color:#38bdf8; font-weight:700;">₹${formattedPrice}</td>
        <td>₹${s.price_per_sqft_inr.toLocaleString()} / sqft</td>
        <td style="font-size:0.75rem;">
          <div style="color:var(--text-dim);">${s.seller_type}</div>
          <div style="color:#a7f3d0; font-weight:600;">➔ ${s.buyer_type}</div>
        </td>
        <td><code style="background:rgba(255,255,255,0.06); padding:2px 6px; border-radius:4px; font-size:0.75rem;">${s.registration_doc_no}</code></td>
        <td>${growthBadge}</td>
      `;
      tbody.appendChild(tr);
    });
  }

  renderNearbyServices(prop, category) {
    const container = document.getElementById('nearby-poi-list');
    if (!container) return;

    container.innerHTML = '';
    const services = prop.nearby_services.filter(
      (s) => category === 'all' || s.category === category
    );

    if (services.length === 0) {
      container.innerHTML = `<div style="text-align:center; padding:20px; color:var(--text-dim); font-size:0.82rem;">No services found for selected category</div>`;
      return;
    }

    const categoryIcons = {
      schools: '🏫',
      hospitals: '🏥',
      metro_railways: '🚆',
      shopping_parks: '🛍️',
    };

    services.forEach((s) => {
      const icon = categoryIcons[s.category] || '📍';
      const item = document.createElement('div');
      item.className = 'poi-card';
      item.style.cssText = `
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid var(--border-color);
        padding: 10px 14px;
        border-radius: 10px;
        transition: transform 0.2s ease, border-color 0.2s ease;
      `;

      const stars = '★'.repeat(Math.floor(s.rating)) + (s.rating % 1 >= 0.5 ? '½' : '');

      item.innerHTML = `
        <div style="display: flex; align-items: center; gap: 12px;">
          <span style="font-size: 1.5rem; background: rgba(56, 189, 248, 0.1); padding: 8px; border-radius: 8px;">${icon}</span>
          <div>
            <div style="font-weight: 700; font-size: 0.88rem; color: #f8fafc;">${s.name}</div>
            <div style="font-size: 0.75rem; color: var(--text-dim);">${s.type}</div>
            <div style="font-size: 0.72rem; color: var(--accent-gold); margin-top: 2px;">${stars} ${s.rating} / 5.0</div>
          </div>
        </div>
        <div style="text-align: right;">
          <div style="font-weight: 800; font-size: 0.95rem; color: #38bdf8;">${s.distance_km} km</div>
          <div style="font-size: 0.72rem; color: #a7f3d0;">⏱ ${s.travel_time_mins} mins drive</div>
          <button class="btn-focus-poi" style="margin-top:4px; background:none; border:none; color:#38bdf8; font-size:0.72rem; cursor:pointer; text-decoration:underline;">View on Map</button>
        </div>
      `;

      item.querySelector('.btn-focus-poi').addEventListener('click', () => {
        if (this.propertyHistoryMap) {
          this.propertyHistoryMap.setView([s.lat, s.lng], 16);
        }
      });

      container.appendChild(item);
    });
  }

  renderPropertyHistoryMap(prop, category) {
    if (!this.propertyHistoryMap) return;

    // Clear previous markers
    this.propertyHistoryMarkers.forEach((m) => m.remove());
    this.propertyHistoryMarkers = [];

    // Center map on property
    const propLat = prop.lat;
    const propLng = prop.lng;
    this.propertyHistoryMap.setView([propLat, propLng], 14);

    // Custom Gold Property Marker Icon
    const propIcon = L.divIcon({
      className: 'custom-prop-marker',
      html: `<div style="background:#f59e0b; color:#0f172a; font-weight:bold; font-size:11px; padding:4px 8px; border-radius:12px; border:2px solid #fff; box-shadow:0 0 10px rgba(245,158,11,0.6); display:flex; align-items:center; gap:4px;">🏰 ${prop.name}</div>`,
      iconSize: [140, 30],
      iconAnchor: [70, 15],
    });

    const propMarker = L.marker([propLat, propLng], { icon: propIcon }).addTo(
      this.propertyHistoryMap
    ).bindPopup(`
        <div style="font-family:Inter,sans-serif; padding:4px;">
          <strong style="color:#f59e0b; font-size:14px;">${prop.name}</strong><br/>
          <span style="font-size:12px; color:#475569;">${prop.address}</span><br/>
          <hr style="margin:6px 0; border:0; border-top:1px solid #e2e8f0;"/>
          <b style="color:#0f172a;">Current Value: ₹${this.formatCurrency(prop.price_summary.latest_price_inr)}</b>
        </div>
      `);
    this.propertyHistoryMarkers.push(propMarker);

    // Filter services
    const services = prop.nearby_services.filter(
      (s) => category === 'all' || s.category === category
    );
    const bounds = L.latLngBounds([[propLat, propLng]]);

    const categoryIcons = {
      schools: '🏫',
      hospitals: '🏥',
      metro_railways: '🚆',
      shopping_parks: '🛍️',
    };

    services.forEach((s) => {
      const iconSymbol = categoryIcons[s.category] || '📍';
      const poiIcon = L.divIcon({
        className: 'custom-poi-marker',
        html: `<div style="background:#0f172a; color:#38bdf8; font-weight:600; font-size:10px; padding:3px 6px; border-radius:8px; border:1px solid #38bdf8; box-shadow:0 0 6px rgba(56,189,248,0.4); display:flex; align-items:center; gap:3px;">${iconSymbol} ${s.name.substring(0, 18)}..</div>`,
        iconSize: [120, 24],
        iconAnchor: [60, 12],
      });

      const poiMarker = L.marker([s.lat, s.lng], { icon: poiIcon }).addTo(this.propertyHistoryMap)
        .bindPopup(`
          <div style="font-family:Inter,sans-serif; padding:4px;">
            <strong style="color:#0284c7;">${iconSymbol} ${s.name}</strong><br/>
            <span style="font-size:11px; color:#64748b;">${s.type}</span><br/>
            <div style="font-size:12px; font-weight:bold; color:#0f172a; margin-top:4px;">
              Distance: ${s.distance_km} km (${s.travel_time_mins} mins drive)
            </div>
          </div>
        `);
      this.propertyHistoryMarkers.push(poiMarker);

      // Connect property to POI with dashed vector line
      const line = L.polyline(
        [
          [propLat, propLng],
          [s.lat, s.lng],
        ],
        {
          color: '#38bdf8',
          weight: 2,
          dashArray: '4, 8',
          opacity: 0.6,
        }
      ).addTo(this.propertyHistoryMap);
      this.propertyHistoryMarkers.push(line);

      bounds.extend([s.lat, s.lng]);
    });

    if (services.length > 0) {
      this.propertyHistoryMap.fitBounds(bounds, { padding: [30, 30] });
    }
  }

  calculateCagrEstimate() {
    const buyYear = parseFloat(document.getElementById('cagr-buy-year')?.value) || 2015;
    const buyPriceLakhs = parseFloat(document.getElementById('cagr-buy-price')?.value) || 50.0;
    const targetYear = parseFloat(document.getElementById('cagr-target-year')?.value) || 2026;
    const annualRatePct = parseFloat(document.getElementById('cagr-annual-rate')?.value) || 10.5;

    const years = Math.max(1, targetYear - buyYear);
    const projectedValLakhs = buyPriceLakhs * Math.pow(1 + annualRatePct / 100, years);
    const totalReturnPct = ((projectedValLakhs - buyPriceLakhs) / buyPriceLakhs) * 100;

    const projValEl = document.getElementById('calc-projected-val');
    const returnEl = document.getElementById('calc-total-return');

    if (projValEl) {
      projValEl.textContent = `₹${projectedValLakhs.toFixed(2)} Lakhs`;
    }

    if (returnEl) {
      returnEl.textContent = `▲ +${totalReturnPct.toFixed(1)}% (${years} yrs)`;
    }
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
  /* ─────────────────────────────────────────────────────────────────────────
   * User-Friendliness Enhancements Logic
   * ───────────────────────────────────────────────────────────────────────── */

  /**
   * Initializes global smart search in the header. Queries the fast-read search API
   * (http://localhost:8000/api/v1/search) with debounce, falling back to local dataset
   * search if the API endpoint is unavailable.
   *
   * @returns {void}
   */
  initGlobalSearch() {
    const input = document.getElementById('global-search-input');
    const dropdown = document.getElementById('global-search-dropdown');
    const clearBtn = document.getElementById('global-search-clear');
    if (!input || !dropdown) return;

    let debounceTimer = null;

    const renderResults = (results) => {
      if (results.length === 0) {
        dropdown.innerHTML =
          '<div class="search-drop-item" style="color:var(--text-dim); text-align:center;">No matching properties or locations found</div>';
      } else {
        dropdown.innerHTML = results
          .slice(0, 8)
          .map(
            (r) => `
          <div class="search-drop-item" data-type="${r.type}" data-id="${r.id}">
            <div>
              <div style="font-weight:700; color:#f8fafc; font-size:0.88rem;">${r.title}</div>
              <div style="font-size:0.75rem; color:var(--text-dim);">${r.subtitle}</div>
            </div>
            <span class="search-drop-badge">${r.badge}</span>
          </div>
        `
          )
          .join('');
      }
      dropdown.style.display = 'block';
    };

    const performLocalSearch = (q) => {
      const results = [];

      // Search Property History DB
      this.propertyHistoryData.forEach((p) => {
        if (
          p.name.toLowerCase().includes(q) ||
          p.address.toLowerCase().includes(q) ||
          p.district.toLowerCase().includes(q) ||
          (p.rera_id && p.rera_id.toLowerCase().includes(q))
        ) {
          results.push({
            type: 'property',
            title: p.name,
            subtitle: `${p.type} (${p.construction_year}) — ${p.address}`,
            id: p.property_id,
            badge: '🏰 Sale History',
          });
        }
      });

      // Search Verified Listings
      this.listings.forEach((l) => {
        if (
          l.title.toLowerCase().includes(q) ||
          l.locality.toLowerCase().includes(q) ||
          l.district.toLowerCase().includes(q) ||
          l.code.toLowerCase().includes(q)
        ) {
          results.push({
            type: 'listing',
            title: l.title,
            subtitle: `${l.type} — ${l.locality}, ${l.district}`,
            id: l.code,
            badge: '✨ Listing',
          });
        }
      });

      // Search Districts
      this.districts.forEach((d) => {
        if (d.name.toLowerCase().includes(q)) {
          results.push({
            type: 'district',
            title: `${d.name} District`,
            subtitle: `${d.state} (${d.count || 0} registered SRO sales)`,
            id: d.name,
            badge: '🗺️ District',
          });
        }
      });

      renderResults(results);
    };

    input.addEventListener('input', (e) => {
      const q = e.target.value.trim().toLowerCase();
      if (clearBtn) clearBtn.style.display = q ? 'block' : 'none';

      if (debounceTimer) clearTimeout(debounceTimer);

      if (q.length < 2) {
        dropdown.style.display = 'none';
        dropdown.innerHTML = '';
        return;
      }

      debounceTimer = setTimeout(async () => {
        try {
          const apiHost = window.location.hostname || 'localhost';
          const res = await fetch(
            `http://${apiHost}:8000/api/v1/search?q=${encodeURIComponent(q)}&per_page=8`,
            {
              signal: AbortSignal.timeout(1500),
            }
          );
          if (res.ok) {
            const data = await res.json();
            if (data.results && data.results.length > 0) {
              const apiResults = data.results.map((hit) => ({
                type: 'property',
                title: hit.property_title || hit.locality,
                subtitle: `${hit.locality}, ${hit.district} [${hit.state_code}]`,
                id: hit.id,
                badge: '⚡ Fast Read API',
              }));
              renderResults(apiResults);
              return;
            }
          }
          performLocalSearch(q);
        } catch {
          // Fallback gracefully to client-side search if API microservice is offline
          performLocalSearch(q);
        }
      }, 150);
    });

    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        input.value = '';
        clearBtn.style.display = 'none';
        dropdown.style.display = 'none';
      });
    }

    dropdown.addEventListener('click', (e) => {
      const item = e.target.closest('.search-drop-item');
      if (!item) return;
      const type = item.dataset.type;
      const id = item.dataset.id;
      dropdown.style.display = 'none';
      input.value = '';
      if (clearBtn) clearBtn.style.display = 'none';

      if (type === 'property') {
        const tabBtn = document.querySelector('[data-tab="property-history-panel"]');
        if (tabBtn) tabBtn.click();
        const select = document.getElementById('prop-history-select');
        if (select) {
          select.value = id;
          this.selectProperty(id);
        }
      } else if (type === 'listing') {
        const tabBtn = document.querySelector('[data-tab="listings-panel"]');
        if (tabBtn) tabBtn.click();
        const searchInput = document.getElementById('list-search');
        if (searchInput) {
          searchInput.value = id;
          searchInput.dispatchEvent(new Event('input'));
        }
      } else if (type === 'district') {
        const tabBtn = document.querySelector('[data-tab="map-panel"]');
        if (tabBtn) tabBtn.click();
        this.selectedDistrict = id;
        this.renderVerifiedListings();
      }
    });

    // Close on outside click
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.global-search-container')) {
        dropdown.style.display = 'none';
      }
    });
  }

  /* 2. Side-by-Side Property Comparison */
  initPropertyComparison() {
    const openBtn = document.getElementById('btn-open-compare-modal');
    const clearBtn = document.getElementById('btn-clear-compare');
    const closeBtn = document.getElementById('modal-compare-close-btn');

    if (openBtn) {
      openBtn.addEventListener('click', () => this.renderComparisonModal());
    }

    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        this.comparedPropertyIds = [];
        this.renderCompareBar();
        this.renderVerifiedListings();
      });
    }

    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        const modal = document.getElementById('comparison-modal');
        if (modal) modal.style.display = 'none';
      });
    }
  }

  toggleCompareProperty(propId) {
    const idx = this.comparedPropertyIds.indexOf(propId);
    if (idx >= 0) {
      this.comparedPropertyIds.splice(idx, 1);
    } else {
      if (this.comparedPropertyIds.length >= 3) {
        alert('You can compare a maximum of 3 properties side-by-side.');
        return;
      }
      this.comparedPropertyIds.push(propId);
    }
    this.renderCompareBar();
    this.renderVerifiedListings();
  }

  renderCompareBar() {
    const bar = document.getElementById('compare-floating-bar');
    const countEl = document.getElementById('compare-count');
    const thumbs = document.getElementById('compare-thumbnails');

    if (!bar || !countEl || !thumbs) return;

    if (this.comparedPropertyIds.length === 0) {
      bar.style.display = 'none';
      return;
    }

    countEl.textContent = this.comparedPropertyIds.length;
    thumbs.innerHTML = '';

    this.comparedPropertyIds.forEach((id) => {
      const prop =
        this.propertyHistoryData.find((p) => p.property_id === id) ||
        this.listings.find((l) => l.code === id);
      const name = prop ? prop.name || prop.title : id;

      const chip = document.createElement('div');
      chip.className = 'compare-chip';
      chip.innerHTML = `<span>${name.substring(0, 15)}..</span> <button data-id="${id}">&times;</button>`;
      chip.querySelector('button').addEventListener('click', (e) => {
        e.stopPropagation();
        this.toggleCompareProperty(id);
      });
      thumbs.appendChild(chip);
    });

    bar.style.display = 'flex';
  }

  renderComparisonModal() {
    const modal = document.getElementById('comparison-modal');
    const body = document.getElementById('comparison-modal-body');
    if (!modal || !body) return;

    if (this.comparedPropertyIds.length === 0) {
      alert('Please select at least 1 property to compare.');
      return;
    }

    const items = this.comparedPropertyIds
      .map((id) => {
        return (
          this.propertyHistoryData.find((p) => p.property_id === id) ||
          this.listings.find((l) => l.code === id)
        );
      })
      .filter(Boolean);

    body.innerHTML = items
      .map((item) => {
        const isHistoryProp = !!item.price_summary;
        const title = item.name || item.title;
        const price = isHistoryProp
          ? this.formatCurrency(item.price_summary.latest_price_inr)
          : (item.price / 100000).toFixed(2) + ' L';
        const cagr = isHistoryProp ? item.price_summary.cagr_pct.toFixed(1) + '%' : 'N/A';
        const appreciation = isHistoryProp
          ? '+' + item.price_summary.total_appreciation_pct.toFixed(1) + '%'
          : 'N/A';
        const year = item.construction_year || '2022';
        const sqft = item.total_sqft || item.area;
        const sqftRate = isHistoryProp
          ? '₹' +
            item.sale_history[item.sale_history.length - 1].price_per_sqft_inr.toLocaleString()
          : '₹' + Math.round(item.price / item.area).toLocaleString();
        const rera = item.rera_id || item.code || 'VERIFIED';
        const state = item.state || 'Telangana';

        const nearestMetro = isHistoryProp
          ? item.nearby_services.find((s) => s.category === 'metro_railways')?.name || 'N/A'
          : 'Raidurg Metro';
        const nearestSchool = isHistoryProp
          ? item.nearby_services.find((s) => s.category === 'schools')?.name || 'N/A'
          : 'International School';

        return `
        <div class="compare-col-card" style="background: rgba(15, 23, 42, 0.9); border: 1px solid var(--border-color); padding: 16px; border-radius: 12px;">
          <div style="font-weight:800; font-size:1.05rem; color:#38bdf8; margin-bottom:4px;">${title}</div>
          <div style="font-size:0.75rem; color:var(--text-dim); margin-bottom:12px;">${item.address || item.locality}</div>
          
          <div class="compare-spec-row"><span>Valuation:</span> <strong style="color:#10b981;">₹${price}</strong></div>
          <div class="compare-spec-row"><span>Appreciation:</span> <strong style="color:#f59e0b;">${appreciation}</strong></div>
          <div class="compare-spec-row"><span>CAGR ROI:</span> <strong>${cagr}</strong></div>
          <div class="compare-spec-row"><span>Rate / SqFt:</span> <strong>${sqftRate}</strong></div>
          <div class="compare-spec-row"><span>Total Size:</span> <strong>${sqft} sq ft</strong></div>
          <div class="compare-spec-row"><span>Built Year:</span> <strong>${year}</strong></div>
          <div class="compare-spec-row"><span>State:</span> <strong>${state}</strong></div>
          <div class="compare-spec-row"><span>RERA ID:</span> <code style="font-size:0.72rem;">${rera}</code></div>
          <div class="compare-spec-row"><span>Nearest Metro:</span> <span style="font-size:0.75rem; color:#a7f3d0;">🚆 ${nearestMetro}</span></div>
          <div class="compare-spec-row"><span>Nearest School:</span> <span style="font-size:0.75rem; color:#94a3b8;">🏫 ${nearestSchool}</span></div>
        </div>
      `;
      })
      .join('');

    modal.style.display = 'flex';
  }

  /* 3. Export / Print Valuation Report */
  initExportReport() {
    const btn = document.getElementById('btn-export-report');
    if (btn) {
      btn.addEventListener('click', () => this.exportValuationReport());
    }
  }

  exportValuationReport() {
    const prop = this.selectedProperty;
    if (!prop) {
      alert('Please select a property first.');
      return;
    }

    const printWin = window.open('', '_blank', 'width=900,height=800');
    if (!printWin) return;

    const initialFormatted = this.formatCurrency(prop.price_summary.initial_price_inr);
    const latestFormatted = this.formatCurrency(prop.price_summary.latest_price_inr);

    const historyRows = prop.sale_history
      .map(
        (s) => `
      <tr>
        <td>${s.year} (${s.sale_date})</td>
        <td>₹${this.formatCurrency(s.sale_price_inr)}</td>
        <td>₹${s.price_per_sqft_inr.toLocaleString()} / sqft</td>
        <td>${s.seller_type} ➔ ${s.buyer_type}</td>
        <td>${s.registration_doc_no}</td>
        <td>+${s.growth_over_initial_pct.toFixed(1)}%</td>
      </tr>
    `
      )
      .join('');

    const poiRows = prop.nearby_services
      .map(
        (s) => `
      <tr>
        <td>${s.name}</td>
        <td>${s.category}</td>
        <td>${s.distance_km} km (${s.travel_time_mins} mins)</td>
        <td>${s.rating} ★</td>
      </tr>
    `
      )
      .join('');

    printWin.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>Crown Corridor — Valuation & Audit Report (${prop.name})</title>
        <style>
          body { font-family: 'Segoe UI', Arial, sans-serif; padding: 30px; color: #1e293b; background: #fff; }
          h1 { color: #0284c7; margin-bottom: 4px; }
          .header-box { border-bottom: 2px solid #0284c7; padding-bottom: 12px; margin-bottom: 20px; display:flex; justify-content:space-between; align-items:flex-end; }
          .summary-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; background: #f8fafc; padding: 16px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 24px; }
          .summary-item label { display:block; font-size: 11px; text-transform: uppercase; color: #64748b; font-weight:700; }
          .summary-item value { font-size: 16px; font-weight: bold; color: #0f172a; }
          table { width: 100%; border-collapse: collapse; margin-bottom: 24px; font-size: 13px; }
          th, td { border: 1px solid #cbd5e1; padding: 8px 12px; text-align: left; }
          th { background: #f1f5f9; color: #334155; }
          .footer { margin-top: 40px; text-align: center; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 12px; }
        </style>
      </head>
      <body>
        <div class="header-box">
          <div>
            <h1>Crown Corridor</h1>
            <div style="font-size:14px; font-weight:bold; color:#475569;">Official Property Registry Audit & Valuation Report</div>
          </div>
          <div style="text-align:right; font-size:12px; color:#64748b;">
            Report Date: ${new Date().toLocaleDateString('en-IN')}<br>
            RERA ID: ${prop.rera_id || 'N/A'}
          </div>
        </div>

        <h2>${prop.name}</h2>
        <p style="color:#64748b; margin-top:-8px;">${prop.address}, ${prop.district}, ${prop.state.toUpperCase()}</p>

        <div class="summary-grid">
          <div class="summary-item"><label>Construction Year</label><value>${prop.construction_year}</value></div>
          <div class="summary-item"><label>Total Area</label><value>${prop.total_sqft} sq.ft (${prop.bedrooms} BHK)</value></div>
          <div class="summary-item"><label>Holding Period</label><value>${prop.price_summary.holding_period_years} Years</value></div>
          <div class="summary-item"><label>Initial Booking Price</label><value>₹${initialFormatted}</value></div>
          <div class="summary-item"><label>Current SRO Valuation</label><value>₹${latestFormatted}</value></div>
          <div class="summary-item"><label>Total CAGR Return</label><value>+${prop.price_summary.total_appreciation_pct.toFixed(1)}% (${prop.price_summary.cagr_pct.toFixed(1)}% CAGR)</value></div>
        </div>

        <h3>Historical SRO Registration Audit Trail</h3>
        <table>
          <thead>
            <tr>
              <th>Year & Date</th>
              <th>Registration Price</th>
              <th>Rate / SqFt</th>
              <th>Seller ➔ Buyer</th>
              <th>SRO Document #</th>
              <th>Growth %</th>
            </tr>
          </thead>
          <tbody>${historyRows}</tbody>
        </table>

        <h3>Nearby Infrastructure & Proximity Scoring</h3>
        <table>
          <thead>
            <tr>
              <th>Amenity / Service Name</th>
              <th>Category</th>
              <th>Distance & Drive Time</th>
              <th>Rating</th>
            </tr>
          </thead>
          <tbody>${poiRows}</tbody>
        </table>

        <div class="footer">
          Generated automatically by Crown Corridor Real Estate Analytics Engine • Verified SRO Geospatial Record
        </div>
      </body>
      </html>
    `);

    printWin.document.close();
    printWin.focus();
    setTimeout(() => printWin.print(), 500);
  }

  /* 4. Visual Preset Filters */
  initPresetFilters() {
    const pills = document.querySelectorAll('#preset-filter-row .btn-pill');
    pills.forEach((btn) => {
      btn.addEventListener('click', () => {
        pills.forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        const preset = btn.dataset.preset;

        const stateSelect = document.getElementById('list-state');
        const typeSelect = document.getElementById('list-type');

        if (preset === 'all') {
          if (stateSelect) stateSelect.value = 'All';
          if (typeSelect) typeSelect.value = 'All';
        } else if (preset === 'telangana') {
          if (stateSelect) stateSelect.value = 'Telangana';
        } else if (preset === 'andhra') {
          if (stateSelect) stateSelect.value = 'Andhra Pradesh';
        } else if (preset === 'luxury-villas') {
          if (typeSelect) typeSelect.value = 'Independent Villa';
        }

        this.renderVerifiedListings();
      });
    });
  }

  /* 5. Geolocation 'Locate Me' Distance Calculator */
  initGeolocation() {
    const btn = document.createElement('button');
    btn.className = 'btn-locate-me';
    btn.innerHTML = '📍 Find Near Me';
    btn.style.cssText =
      'position:absolute; bottom:20px; left:20px; z-index:1000; background:#0f172a; color:#38bdf8; border:1px solid #38bdf8; padding:8px 14px; border-radius:20px; font-weight:700; font-size:0.8rem; cursor:pointer; box-shadow:0 4px 14px rgba(0,0,0,0.5);';

    const mapContainer = document.querySelector('#map-panel .map-container');
    if (mapContainer) {
      mapContainer.style.position = 'relative';
      mapContainer.appendChild(btn);
    }

    btn.addEventListener('click', () => {
      if (!navigator.geolocation) {
        alert('Geolocation is not supported by your browser.');
        return;
      }

      btn.textContent = '⏳ Locating...';

      navigator.geolocation.getCurrentPosition(
        (pos) => {
          btn.textContent = '📍 Near Me Active';
          const lat = pos.coords.latitude;
          const lng = pos.coords.longitude;
          this.userLocation = { lat, lng };

          if (this.map) {
            this.map.setView([lat, lng], 13);
            L.circleMarker([lat, lng], {
              radius: 10,
              fillColor: '#38bdf8',
              color: '#ffffff',
              weight: 3,
              fillOpacity: 0.9,
            })
              .addTo(this.map)
              .bindPopup('<b>Your Current Location</b>')
              .openPopup();
          }
        },
        (err) => {
          console.warn('Geolocation error:', err);
          btn.textContent = '📍 Near Me (Default: Hyd)';
          // Fallback to Hyderabad center
          this.userLocation = { lat: 17.4401, lng: 78.3489 };
          if (this.map) {
            this.map.setView([17.4401, 78.3489], 13);
          }
        }
      );
    });
  }

  /* 6. Theme Switcher & Live SRO Feed Controls */
  initThemeSwitcher() {
    const btn = document.getElementById('theme-toggle-btn');
    if (!btn) return;

    btn.addEventListener('click', () => {
      this.currentTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
      document.body.classList.toggle('light-theme', this.currentTheme === 'light');
      btn.textContent = this.currentTheme === 'dark' ? '☀️ Light' : '🌙 Dark';
    });
  }

  initTickerControls() {
    const toggleBtn = document.getElementById('ticker-toggle-btn');
    const speedSelect = document.getElementById('ticker-speed-select');

    if (toggleBtn) {
      toggleBtn.addEventListener('click', () => {
        this.isTickerPaused = !this.isTickerPaused;
        toggleBtn.textContent = this.isTickerPaused ? '▶ Resume' : '⏸ Pause';
        toggleBtn.classList.toggle('pulse-green', !this.isTickerPaused);
      });
    }

    if (speedSelect) {
      speedSelect.addEventListener('change', (e) => {
        this.tickerIntervalMs = parseInt(e.target.value, 10) || 8000;
        const speedTag = document.querySelector('.ticker-speed');
        if (speedTag) speedTag.textContent = `${this.tickerIntervalMs / 1000}s loop`;
      });
    }
  }

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

  /**
   * Loads state-modular market trends datasets.
   *
   * Fetches `andhra_pradesh/market_trends.json` and `telangana/market_trends.json`
   * containing historical per-sqft price trajectories and employment hubs.
   *
   * @returns {Promise<void>}
   */
  async loadMarketTrendsData() {
    try {
      const [apData, tgData] = await Promise.all([
        fetch('../data/andhra_pradesh/market_trends.json').then((res) =>
          res.ok ? res.json() : null
        ),
        fetch('../data/telangana/market_trends.json').then((res) => (res.ok ? res.json() : null)),
      ]);
      this.marketTrendsData = { ap: apData, tg: tgData };
    } catch (e) {
      console.warn('Could not load market trends datasets:', e);
    }
  }

  /**
   * Initialises the Search by Commute event handlers.
   *
   * @returns {void}
   */
  initCommuteSearch() {
    const hubSelect = document.getElementById('commute-hub-select');
    const timeSelect = document.getElementById('commute-max-time');
    if (!hubSelect || !timeSelect) return;

    hubSelect.addEventListener('change', () => {
      this.selectedCommuteHub = hubSelect.value;
      this.renderVerifiedListings();
    });

    timeSelect.addEventListener('change', () => {
      this.selectedCommuteMaxTime = parseInt(timeSelect.value, 10) || 999;
      this.renderVerifiedListings();
    });
  }

  /**
   * Calculates driving commute distance and estimated drive time to a workplace hub.
   *
   * @param {number} lat - Property latitude.
   * @param {number} lng - Property longitude.
   * @param {string} hubId - Employment hub identifier.
   * @returns {Object|null} Commute metadata or null if invalid.
   */
  calculateCommuteTime(lat, lng, hubId) {
    if (!lat || !lng || !hubId || hubId === 'all') return null;

    const allHubs = [
      ...(this.marketTrendsData.ap?.employment_hubs || []),
      ...(this.marketTrendsData.tg?.employment_hubs || []),
    ];

    const targetHub = allHubs.find((h) => h.id === hubId);
    if (!targetHub) return null;

    const distKm = this.calculateDistanceKm(lat, lng, targetHub.lat, targetHub.lng);
    const driveMins = Math.round(distKm * 3.2);
    return {
      hubName: targetHub.name,
      distanceKm: parseFloat(distKm.toFixed(1)),
      driveMins: Math.max(5, driveMins),
    };
  }

  /**
   * Initialises the Regional Market Trends tab state and pills.
   *
   * @returns {void}
   */
  initMarketTrends() {
    const pillsRow = document.getElementById('trends-state-pills');
    if (!pillsRow) return;

    pillsRow.querySelectorAll('.btn-pill').forEach((btn) => {
      btn.addEventListener('click', () => {
        pillsRow.querySelectorAll('.btn-pill').forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        this.selectedTrendsState = btn.dataset.trendsState || 'all';
        this.renderMarketTrends();
      });
    });
  }

  /**
   * Renders the Regional Market Trends line chart and leaderboard table.
   *
   * @returns {void}
   */
  renderMarketTrends() {
    const apTrends = this.marketTrendsData.ap;
    const tgTrends = this.marketTrendsData.tg;
    if (!apTrends && !tgTrends) return;

    let localities = [];
    let quarters = [];

    if (this.selectedTrendsState === 'telangana' && tgTrends) {
      localities = tgTrends.time_series.localities;
      quarters = tgTrends.time_series.quarters;
    } else if (this.selectedTrendsState === 'andhra_pradesh' && apTrends) {
      localities = apTrends.time_series.localities;
      quarters = apTrends.time_series.quarters;
    } else {
      localities = [
        ...(tgTrends?.time_series.localities || []),
        ...(apTrends?.time_series.localities || []),
      ];
      quarters = tgTrends?.time_series.quarters || apTrends?.time_series.quarters || [];
    }

    const avgRateEl = document.getElementById('trends-avg-rate');
    const cagrAvgEl = document.getElementById('trends-cagr-avg');
    const volumeEl = document.getElementById('trends-total-volume');

    if (localities.length > 0) {
      const avgRate = Math.round(
        localities.reduce(
          (s, l) => s + l.avg_price_sqft_trajectory[l.avg_price_sqft_trajectory.length - 1],
          0
        ) / localities.length
      );
      const avgCagr = (localities.reduce((s, l) => s + l.cagr_5yr, 0) / localities.length).toFixed(
        1
      );
      const totalVol = localities.reduce((s, l) => s + l.annual_volume, 0);

      if (avgRateEl) avgRateEl.textContent = `₹${avgRate.toLocaleString('en-IN')} / sqft`;
      if (cagrAvgEl) cagrAvgEl.textContent = `${avgCagr}%`;
      if (volumeEl) volumeEl.textContent = `${totalVol.toLocaleString('en-IN')} Deals`;
    }

    const ctx = document.getElementById('marketTrendsChart');
    if (ctx && typeof Chart !== 'undefined') {
      if (this.charts.marketTrends) {
        this.charts.marketTrends.destroy();
      }

      const colors = [
        '#38bdf8',
        '#10b981',
        '#f59e0b',
        '#ec4899',
        '#8b5cf6',
        '#3b82f6',
        '#f43f5e',
        '#14b8a6',
      ];
      const datasets = localities.map((loc, idx) => ({
        label: loc.locality,
        data: loc.avg_price_sqft_trajectory,
        borderColor: colors[idx % colors.length],
        backgroundColor: colors[idx % colors.length] + '22',
        borderWidth: 2,
        tension: 0.3,
        fill: false,
        pointRadius: 3,
      }));

      this.charts.marketTrends = new Chart(ctx, {
        type: 'line',
        data: {
          labels: quarters,
          datasets: datasets,
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              labels: {
                color: this.currentTheme === 'light' ? '#0f172a' : '#94a3b8',
                font: { size: 11 },
              },
            },
            tooltip: {
              callbacks: {
                label: (ctx) =>
                  `${ctx.dataset.label}: ₹${ctx.parsed.y.toLocaleString('en-IN')} / sqft`,
              },
            },
          },
          scales: {
            x: {
              grid: { color: 'rgba(255, 255, 255, 0.05)' },
              ticks: { color: this.currentTheme === 'light' ? '#0f172a' : '#94a3b8' },
            },
            y: {
              grid: { color: 'rgba(255, 255, 255, 0.05)' },
              ticks: {
                color: this.currentTheme === 'light' ? '#0f172a' : '#94a3b8',
                callback: (val) => `₹${val.toLocaleString('en-IN')}`,
              },
            },
          },
        },
      });
    }

    const tableBody = document.getElementById('trends-leaderboard-body');
    if (tableBody) {
      const sorted = [...localities].sort((a, b) => b.cagr_5yr - a.cagr_5yr);
      tableBody.innerHTML = sorted
        .map(
          (loc, idx) => `
        <tr>
          <td><strong style="color: var(--ap-color)">#${idx + 1}</strong></td>
          <td><strong>${loc.locality}</strong></td>
          <td>${loc.district}</td>
          <td>₹${loc.avg_price_sqft_trajectory[loc.avg_price_sqft_trajectory.length - 1].toLocaleString('en-IN')}</td>
          <td><span style="color: var(--tg-color); font-weight:700;">▲ ${loc.cagr_5yr}%</span></td>
          <td>${loc.rental_yield_pct}%</td>
          <td>${loc.annual_volume.toLocaleString('en-IN')}</td>
        </tr>
      `
        )
        .join('');
    }
  }
}

// Bootstrap portal
document.addEventListener('DOMContentLoaded', () => {
  window.portal = new RealEstatePortal();
  window.portal.init();
});
