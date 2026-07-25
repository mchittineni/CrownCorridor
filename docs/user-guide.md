# Crown Corridor — User Guide

> **Real Estate at Your Fingertips** — Welcome to **Crown Corridor**! This guide explains all platform features, property history tracking, side-by-side comparison, valuation reports, and search tools. 🇮🇳🏙️

---

## 🌟 What is Crown Corridor?

Crown Corridor is a real-time discovery portal designed to help buyers, investors, and agents evaluate real estate across **Andhra Pradesh** and **Telangana**.

It combines:

1. **🔍 Global Header Smart Search**: Instant search with autocomplete for properties, colonies, districts, and RERA IDs.
2. **⚖️ Property Comparison Tool**: Side-by-side spec comparison modal for up to 3 properties.
3. **🏰 Complete Property Sale History**: State-modular registry audit tracking every sale since construction with CAGR returns.
4. **🖨️ One-Click Valuation Report**: Printable audit summary with historical price charts, SRO document numbers, and infrastructure scores.
5. **📍 Nearby Infrastructure Explorer**: Proximity ratings and driving times for schools, hospitals, metro stations, and parks.
6. **🔴 Live SRO Ticker**: Real-time property registration stream with pause/resume and speed controls.
7. **🔒 Zero-PII Privacy Protection**: Scrubbed, anonymized transaction data with strict role-based classifications.

---

## 🧭 How to Use the Portal

### 1. 🔍 Global Smart Search Bar (Header)

- **Where to find it**: Located prominently at the top of the header.
- **How it works**: Type any property name (e.g. _"Cyber Heights"_, _"Sea Breeze"_), colony (e.g. _"Gachibowli"_, _"Beach Road"_), or district (_"Visakhapatnam"_, _"Rangareddy"_). Click any autocomplete item to jump directly to its tab and focus the property.

### 2. 🏰 Property Sale History & Infrastructure Explorer

- **Where to find it**: Click the **Property Sale History & Infrastructure** tab.
- **How it works**:
  - **Cascading Hierarchy Selector**: Select **State** (`Telangana` or `Andhra Pradesh`) ➔ **District** ➔ **Mandal / Taluk** ➔ **Property List**.
  - **Metric Highlight Card**: View construction year, total area (sq ft), RERA ID, initial booking price, current valuation, and total appreciation %.
  - **Price Growth Chart**: Interactive Chart.js timeline graph showing per-sqft price trajectory over time.
  - **SRO Registration Audit Table**: Complete list of all historical sales with document numbers, transaction dates, sale prices, per-sqft rates, and anonymized buyer/seller types.
  - **Nearby Infrastructure List**: Filter by _Schools_, _Hospitals_, _Metro/Railways_, or _Parks/Shopping_ to view distance in km, commute times, and ratings:
    - **`📍 Focus Map`**: Instantly centers and zooms the interactive map on the selected POI.
    - **`🗺️ Google Maps ↗`**: Opens turn-by-turn driving directions in a new tab on Google Maps.
  - **🖨️ Export Audit Report**: Click to open a clean, print-ready valuation report.

### 3. ⚖️ Property Comparison Tool

- **Where to find it**: Click **`+ Compare`** on any verified listing card.
- **How it works**:
  - Select up to 3 properties. A floating **Compare Bar** appears at the bottom.
  - Click **Compare Side-by-Side** to open a modal comparing Valuation, Rate / SqFt, Total Area, Built Year, CAGR ROI, RERA ID, and nearest Metro/School distances.

### 4. 🚗 Search by Commute (Commute Time Finder)

- **Where to find it**: Top of the **Verified Listings** tab in the **Search by Commute** bar.
- **How it works**:
  - Select your workplace hub (e.g. _HITECH City & Cyber Towers_, _Financial District Nanakramguda_, _Gachibowli Knowledge City_, _Rushikonda IT Hill_, _Amaravati Admin Core_).
  - Select max acceptable driving time (_Within 15 mins_, _Within 30 mins_, _Within 45 mins_).
  - Listings automatically filter to show properties within your desired driving radius with a **`🚗 Commute Badge`** (e.g. `🚗 18 mins to HITECH City (5.6 km)`).

### 5. 📈 Regional Market Trends & Price Index Charts

- **Where to find it**: Click the **📈 Regional Market Trends** tab.
- **How it works**:
  - View quarterly price per sqft trajectories (2016-2026) across top localities in AP and Telangana.
  - Filter trends using state toggle pills (_Combined Regional_, _Telangana Hubs_, _Andhra Pradesh Hubs_).
  - Inspect macro benchmark cards: **Average Rate / SqFt**, **5-Year Avg CAGR Return**, and **Annual Tx Volume**.
  - Review the **Top Appreciating Localities Leaderboard** ranked by 5-year CAGR appreciation % and rental yield %.

### 6. ✨ Verified Listings & Visual Filters

- **Where to find it**: Click the **Verified Listings** tab.
- **How it works**: Use preset pills (_"Near Metro"_, _"High CAGR > 10%"_, _"Luxury Villas"_, _"AP"_, _"TS"_) or standard dropdowns to filter properties by budget and category.

### 5. 📍 GPS "Find Near Me"

- **Where to find it**: Click **📍 Find Near Me** on the map overlay.
- **How it works**: Requests browser geolocation to center the map on your current coordinates and calculate real-time distances to properties and nearby services.

### 6. 🧮 Stamp Duty & Guidance Values

- **Stamp Duty Calculator**: Calculates exact tax breakdown (AP combined 7.5%, TS combined 6.0%).
- **Government Guidance Value Directory**: Look up official minimum guidance rates per sq yard or sq ft by mandal.

---

## 🔒 Privacy & Data Protection

Crown Corridor strictly enforces privacy compliance:

- **No Customer PII**: Customer personal names and personal identity numbers are strictly excluded from dataset files.
- **Role-Based Classifications**: Transactions exclusively display anonymized role types (e.g. `Private Individual Owner`, `Commercial Property Developer`, `Institutional Realty Fund`).

---

## 💻 Running Locally

```bash
# Serve from repo root
python3 -m http.server 8080
```

Open **[http://localhost:8080/app/](http://localhost:8080/app/)**.
