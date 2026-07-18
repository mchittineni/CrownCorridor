# Crown Corridor — User Guide

> Welcome to **Crown Corridor**! This guide is written for home buyers, landowners, real estate agents, and anyone who wants to understand how the platform works without needing to understand code. 🇮🇳🏙️

---

## 🌟 What is Crown Corridor?

Crown Corridor is a real-time portal that helps you monitor, search, and verify real estate transactions and property boundaries across **Andhra Pradesh** and **Telangana**. 

Think of it as a **digital control room** for property. It combines:
1. **Live SRO Ticker**: A live-updating list of property registrations happening right now at Sub-Registrar Offices (SROs).
2. **Verified Property Grid**: A list of actual properties for sale/rent that have been cross-checked by SRO agents for validity.
3. **Interactive Map**: A visual map showing where transaction volumes are highest (hot spots) and where individual properties are located.
4. **Official Boundary Explorer**: A tool that lets you look up a specific village and see the exact shape of land parcels (plots) with their official government survey numbers.

---

## 🧭 How to Use the Portal (Tab by Tab)

The portal is split into **five main tabs** located in the sidebar (or top menu on mobile). Here is how you can use each one:

### 1. Market Overview (Dashboard & Map)
* **What you see**: A large interactive map on the left and a live transaction ticker on the right.
* **How to use it**:
  * **Map Color Coding**: Districts on the map are shaded in blue. **Darker blue** districts have higher transaction activity, while **lighter blue** districts have less. This helps you identify real estate hotspots instantly.
  * **Listings on Map**: Blue circular markers on the map indicate verified property listings. Click any marker to see details and contact an agent.
  * **Live Ticker**: Watch the right-hand panel update in real-time as property registrations are simulated from various Sub-Registrar Offices.

### 2. Verified Listings (Find Properties)
* **What you see**: A grid of property cards showing plots, flats, villas, agricultural land, and commercial spaces.
* **How to use it**:
  * **Filters**: Use the dropdown menus at the top to filter by State (Andhra Pradesh vs. Telangana) or Property Type.
  * **Search Bar**: Type the name of a district or locality (e.g., "Visakhapatnam" or "Guntur") to filter listings matching that text.
  * **Verification Badges**: Every listing has a green checkmark indicating that its location and survey number have been validated.
  * **Contacting an Agent**: Click **Contact Agent** on any property card to open a pre-filled inquiry form. Submitting this form sends an inquiry toast indicating the broker has been notified.

### 3. Geospatial Boundary Explorer (Verify Plot Survey Numbers)
* **What you see**: A cascading location selector and a dedicated map showing land boundaries.
* **How to use it**:
  * **Drill Down Selector**: Select a State → Select a District → Select a Mandal (sub-district) → Select a Village.
  * **Automatic Navigation**: Once you select a village, the map automatically flies directly to that village's center.
  * **Official Land Parcels (Cadastral Layer)**: Zoom in past level 11. You will see thin blue outline borders showing the exact physical shapes of individual land plots. When zoomed in further, the government survey numbers (e.g. `124/1`) appear inside the shapes.
  * **Civic Amenities**: Look at the sidebar to see how close the selected village is to essential public resources like Primary Health Centers, High Schools, Banks, and agricultural Mandi markets.
  * **Survey Number Chip List**: Click any of the survey chips in the sidebar to simulate highlighting and centering on that specific plot.

### 4. Stamp Duty & Guidance Values (Financial Calculators)
* **What you see**: Two tools to help you calculate official registration fees and look up land value estimates.
* **How to use them**:
  * **Stamp Duty Calculator**: Select your state, select your property type, and enter the property transaction value (in Rupees). The tool automatically calculates:
    * **Stamp Duty**: The tax paid to the state government.
    * **Transfer Duty**: Local body transfer charges.
    * **Registration Fee**: The fee to record the deed.
    * *Notice*: AP has a combined rate of **7.5%**, while Telangana has a rate of **6.0%**.
  * **Government Guidance Value Directory**: Select a state and a district, then click **Search**. The table displays the official minimum guidance value per square yard (for plots) or per square foot (for flats) in each mandal. This is the minimum value at which a property can legally be registered.

### 5. Developer API Console (For Software Developers)
* **What you see**: A query builder and a console displaying code.
* **How to understand it**: 
  * If you are a business or software developer wanting to feed this real estate data into your own company website, you can use this tab to test data queries and configure instant notifications (webhooks) for high-value transactions.

---

## ⚙️ How the System Works in the Background

To keep the platform updated without humans having to manually type in new files every week, Crown Corridor uses **automation pipelines** run by GitHub Actions:

```
[Government Open Data (data.gov.in)]
                │
                ▼ (Weekly Automatic Fetch)
    [Background Data Pipeline] ──► (Validates Structure & Coordinates)
                │
                ▼ (Auto-Sync)
      [GitHub Pages Server] ──► (Updates Deployed Web App)
```

1. **Scheduled Fetcher (`pipeline/fetch_sro.py`)**: Every week, a script automatically runs to check for updates.
2. **Validator (`pipeline/validate_data.py`)**: Before any new data is published, a data integrity checker runs 23 separate automated tests to make sure there are no typos, missing files, or incorrect coordinates.
3. **Auto-Deployment**: Once the tests pass, the updated data is pushed to the server, and the live map updates automatically.

---

## 🚀 How to Run the Portal on Your Computer

You do not need to install complex databases or programming tools to run the portal locally. Follow these 2 simple steps:

1. **Download the Repository**:
   Click the green **Code** button on the GitHub page and select **Download ZIP**, then extract the folder on your computer.
2. **Start a Local Server**:
   Because web browsers block files from loading directly from your hard drive for security reasons (CORS blocks), you must serve the folder. 
   * On **Mac/Linux**, open Terminal, navigate to the folder, and run:
     ```bash
     python3 -m http.server 8080
     ```
   * On **Windows**, open Command Prompt, navigate to the folder, and run the same command:
     ```cmd
     python -m http.server 8080
     ```
3. **Open Your Browser**:
   Go to **[http://localhost:8080/app/](http://localhost:8080/app/)** to view and interact with the portal live.
