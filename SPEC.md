# Sathapana Agricultural Credit Early Warning Platform

## Specification Document — PoC v1.0

**Date:** September 2026
**Status:** Draft for Management Review
**Classification:** Internal — Innovation Lab

**Acronyms**
```
core geospatial technologies: GIS (Geographic Information Systems), GPS (Global Positioning System), and Remote Sensing

Sentinel-1 and Sentinel-2 are specific satellite missions that supply raw remote sensing data

Sentinel-1 is an active radar satellite mission. penetrates clouds and darkness to capture all-weather images of the Earth's surface, making it ideal for flood mapping and ground deformation tracking

Sentinel-2 is a passive optical satellite mission. captures high-resolution multispectral imagery in visible and infrared wavelengths, widely used for monitoring vegetation, agriculture, and land cover
```

```
Sentinel-1 (Synthetic Aperture Radar) : Radar Imaging - uses active microwave pulses to measure surface properties regardless of weather or lighting. 

Sentinel-2 : Optical Imaging - works like a standard camera by capturing reflected sunlight
```

```
GIS : Geographic Information System analyzes and visualizes that spatial data to drive real-world decisions
GIS (The Software): Manages, models, and processes raster maps and vector data (points, lines, polygons) to interpret local impacts

GPS : The Global Positioning System is a satellite-based navigation network that provides precise location, velocity, and time synchronization anywhere on Earth
GPS tells you where an object is located

Remote sensing : Remote sensing collects raw data about the Earth's surface from a distance using satellites, drones, or aircraft
Remote Sensing (The Camera): Gathers raw images, pixels, and spectral bands across large regional or global scales.
```
---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Proposed Solution](#3-proposed-solution)
4. [PoC Scope & Objectives](#4-poc-scope--objectives)
5. [3-Stage PoC Architecture](#5-3-stage-poc-architecture)
6. [Data Sources & Integration](#6-data-sources--integration)
7. [Technical Architecture](#7-technical-architecture)
8. [Farm Mapping — Stage 1](#8-farm-mapping--stage-1)
9. [Crop Health Monitoring — Stage 2](#9-crop-health-monitoring--stage-2)
10. [Credit Early Warning — Stage 3](#10-credit-early-warning--stage-3)
11. [Risk Model Design](#11-risk-model-design)
12. [Dashboard & Alert System](#12-dashboard--alert-system)
13. [Pilot Design — Control Group](#13-pilot-design--control-group)
14. [Success Metrics & KPIs](#14-success-metrics--kpis)
15. [Implementation Plan — 16 Weeks](#15-implementation-plan--16-weeks)
16. [Team & Roles](#16-team--roles)
17. [Budget Estimate](#17-budget-estimate)
18. [Risk & Mitigation](#18-risk--mitigation)
19. [Governance & Ethics](#19-governance--ethics)
20. [Post-PoC Roadmap](#20-post-poc-roadmap)
21. [Appendix](#21-appendix)
22. [Feasibility Assessment](#22-feasibility-assessment--will-this-work-for-sathapana)
23. [GPS Data Collection](#23-gps-data-collection--how-to-get-farm-coordinates)
24. [Do Banks Need External Data?](#24-do-banks-really-need-external-data-for-farmers)
25. [Mandatory External Data Sources](#25-mandatory-external-data-sources-for-sathapana)
26. [How to Get Cambodian Sentinel Data](#26-how-to-get-cambodian-data-from-sentinel-2-and-sentinel-1)
27. [Automated GEE Ingestion Pipeline](#27-automated-gee-data-ingestion-pipeline)
12. [Dashboard & Alert System](#12-dashboard--alert-system)
13. [Pilot Design — Control Group](#13-pilot-design--control-group)
14. [Success Metrics & KPIs](#14-success-metrics--kpis)
15. [Implementation Plan — 16 Weeks](#15-implementation-plan--16-weeks)
16. [Team & Roles](#16-team--roles)
17. [Budget Estimate](#17-budget-estimate)
18. [Risk & Mitigation](#18-risk--mitigation)
19. [Governance & Ethics](#19-governance--ethics)
20. [Post-PoC Roadmap](#20-post-poc-roadmap)
21. [Appendix](#21-appendix)

---

## 1. Executive Summary

### What is this?

An **AI-powered agricultural credit early warning platform** that:

- Creates a digital profile of each agricultural borrower's farm using satellite imagery
- Continuously monitors crop health, drought, and flood conditions via remote sensing
- Combines environmental signals with Sathapana's loan and transaction data
- Identifies borrowers at elevated risk of repayment stress **before delinquency occurs**
- Enables proactive Relationship Manager intervention

### Why now?

- Sathapana has significant agricultural/SME lending exposure in Cambodia
- FAO has already demonstrated AI-based rice-boundary recognition using Sentinel-2 data in Cambodia
- A Cambodian agri-fintech is already using satellite data to help lenders assess farm conditions
- Sathapana participated in an ADB agricultural value-chain project in Cambodia
- World Bank assessments identify agricultural credit scoring as a validated digital-agriculture use case in Cambodia

### What is the business case?

**Before:**

```
Farmer → Loan → Crop failure → Missed payment → NPL → Collections → Loss
```

**With the platform:**

```
Farmer → Loan → Satellite monitoring + Weather + Cash-flow monitoring
    → Early warning → RM intervention → Restructuring/assistance/insurance
    → Potentially avoid NPL
```

### PoC headline target

**Can we identify financially stressed agricultural borrowers 30+ days earlier than the current process?**

---

## 2. Problem Statement

### Current state

When Sathapana lends to agricultural borrowers:

1. Loan officer visits farm (one-time, at origination)
2. Farmer provides crop/area information (self-reported, not always validated)
3. Loan is disbursed
4. Bank monitors repayment schedule
5. If payment is missed → standard collections process

### The gap

There is **no continuous visibility** into what is happening on the farm between origination and maturity.

By the time a payment is missed:

- The crop may have failed months earlier
- The farmer may already be in financial distress
- Recovery options are limited
- NPL classification may be inevitable

### The opportunity

Satellite imagery, weather data, and AI can fill this gap — providing the bank with ongoing signals about:

- Whether the farm exists and matches loan records
- Whether the crop is developing normally
- Whether drought, flood, or other stress is affecting the farm
- Whether these environmental signals correlate with financial stress

This creates an **early warning** window — weeks or months before a missed payment.

---

## 3. Proposed Solution

### System name

**Sathapana Agricultural Risk Platform (SARP)**

### Tagline

*AI-powered agricultural credit early warning for proactive risk management*

### Core concept

```
                    SATHAPANA AGRICULTURAL RISK PLATFORM

 Farmer / Loan Data ───────┐
                           │
 Farm GPS / Polygon ───────┤
                           ▼
                    ┌───────────────┐
                    │ STAGE 1       │
                    │ FARM MAPPING  │
                    └───────┬───────┘
                            │
                       Farm polygon
                       Crop / area
                            │
                            ▼
                    ┌───────────────┐
                    │ STAGE 2       │
                    │ CROP HEALTH   │
                    └───────┬───────┘
                            │
                  Crop-health indicators
                  drought / flood / stress
                            │
                            ▼
                    ┌───────────────┐
                    │ STAGE 3       │
                    │ LOAN EARLY    │
                    │ WARNING       │
                    └───────┬───────┘
                            │
                            ▼
                 Agricultural Risk Score
                            │
               ┌────────────┼────────────┐
               ▼            ▼            ▼
             Green        Amber          Red
             Normal       Watch          Action
```

### Not this

This is **not** a standalone satellite imaging project. It is a **credit risk enhancement platform** that uses satellite/remote sensing as one of several data inputs.

The technical stack combines:

- Remote sensing (Sentinel-1, Sentinel-2)
- Computer vision (crop segmentation, boundary detection)
- GIS (geospatial analysis, flood mapping)
- Machine learning (crop health models, credit risk models)
- Data engineering (feature pipelines, time-series)
- Banking data integration (CBS, loan system, transactions)

---

## 4. PoC Scope & Objectives

### PoC definition

A **12–16 week pilot** with 500–1,000 agricultural borrowers in 1–2 Cambodian provinces.

### PoC objectives

| # | Objective | Stage |
|---|-----------|-------|
| 1 | Prove we can locate and map farms from satellite data | Stage 1 |
| 2 | Prove we can detect and monitor crop health | Stage 2 |
| 3 | Prove environmental signals correlate with financial stress | Stage 3 |
| 4 | Prove early warning lead time exceeds 30 days | Stage 3 |
| 5 | Establish a control group for business-impact measurement | Stage 3 |
| 6 | Build internal capability and stakeholder confidence | All |

### PoC non-objectives

The PoC will **NOT**:

- Make automated lending decisions
- Replace human judgment in credit assessment
- Scale to all agricultural borrowers during the pilot
- Support all crop types (rice only in Phase 1)
- Achieve production-grade reliability

### What "success" looks like

**Technical success:**

- ≥90% of pilot farms successfully mapped
- ≥80% crop health classification accuracy
- ≥30-day early warning lead time
- Risk model AUC ≥ 0.75

**Business success:**

- ≥70% of high-risk borrowers identified before delinquency
- <20% false-positive rate
- RM team adopts the dashboard and acts on alerts
- Management sees a credible path to scale

---

## 5. 3-Stage PoC Architecture

### Stage 1: Farm Mapping

**Question answered:** *"Where is the farm, and what is being cultivated?"*

```
Sathapana Loan System
        │
        ├── Farmer
        ├── Loan
        └── Agricultural loan
                │
                ▼
        Farm Mapping Service
                ▲
                │
        GPS / Mobile App
                │
                ▼
        Farm Polygon
                │
        ┌───────┴────────┐
        ▼                ▼
   Sentinel-2        Sentinel-1
        │                │
        └───────┬────────┘
                ▼
          GIS / CV Model
                │
                ▼
        Digital Farm Profile
```

**Inputs:**

- Farmer ID, Loan ID
- GPS coordinates (collected via mobile app or RM)
- Sentinel-2 optical imagery
- Sentinel-1 SAR imagery
- Crop type (from farmer/RM)

**Outputs:**

- Farm boundary polygon
- Cultivated area (hectares)
- Crop classification (rice / other)
- Digital farm profile record

**Duration:** Weeks 2–7

---

### Stage 2: Crop Health Monitoring

**Question answered:** *"Is the crop developing normally?"*

**Inputs:**

- Farm polygon from Stage 1
- Time-series Sentinel-2 imagery (every 5 days)
- Time-series Sentinel-1 SAR imagery (every 6–12 days)
- Rainfall data (CHIRPS or local weather stations)
- Temperature data
- Historical crop cycle data

**Processing:**

```
Sentinel-2 imagery
        │
        ▼
   Cloud masking
        │
        ▼
   Spectral indices (NDVI, NDWI, EVI)
        │
        ▼
   Per-farm zonal statistics
        │
        ▼
   Time-series construction
        │
        ▼
   Crop-growth curve fitting
        │
        ▼
   Deviation detection
        │
        ▼
   Crop Health Score
```

**Outputs per farm:**

| Metric | Description |
|--------|-------------|
| NDVI | Current vegetation index |
| NDVI deviation | Current vs. historical/historical normal |
| NDWI | Water/moisture index |
| Growth stage | Vegetative / Reproductive / Maturity / Fallow |
| Flood exposure | Whether farm shows flood signatures |
| Drought stress | Derived from NDVI decline + low rainfall |
| Crop Health Score | Composite score (0–100) |
| Status | Green / Yellow / Orange / Red |

**Duration:** Weeks 6–11

---

### Stage 3: Credit Early Warning

**Question answered:** *"Could crop stress affect repayment?"*

```
             SATELLITE
                 │
                 ▼
          Crop Health Score
                 │
                 │
WEATHER ────────┤
                 │
FARM DATA ──────┤
                 │
TRANSACTIONS ───┤
                 │
LOAN DATA ──────┤
                 │
CREDIT HISTORY ─┤
                 ▼
        Agricultural Risk Model
                 │
                 ▼
       Probability of Repayment
              Difficulty
                 │
       ┌─────────┼─────────┐
       ▼         ▼         ▼
      Green    Amber       Red
      Normal   Watch     Action
```

**Duration:** Weeks 9–15

---

## 6. Data Sources & Integration

### External data sources

| Data Source | Provider | Cost | Update Frequency | Purpose |
|-------------|----------|------|------------------|---------|
| Sentinel-2 optical | ESA / Copernicus | Free | Every 5 days | Crop health, NDVI, land cover |
| Sentinel-1 SAR | ESA / Copernicus | Free | Every 6–12 days | Flood detection, cloud-penetrating observation |
| CHIRPS rainfall | UCSB / CHC | Free | Daily | Drought/flood indicators |
| ERA5 temperature | ECMWF | Free | Hourly (aggregated) | Heat/cold stress |
| MODIS land cover | NASA | Free | 16-day | Historical baselines |
| Cambodia admin boundaries | OCHA / GADM | Free | Static | Province/district mapping |
| Mekong River Commission flood data | MRC | Free | Near-real-time | Flood alerts |

### Sathapana internal data

| Data Source | System | Purpose |
|-------------|--------|---------|
| Farmer profile | CBS / CRM | Identify borrower, demographics |
| Loan record | Loan system | Loan amount, term, repayment schedule |
| Repayment history | Loan system | DPD, missed payments, restructuring |
| Account transactions | CBS / Core banking | Cash flow, deposits, withdrawals |
| KHQR/POS transactions | Payment system | Merchant revenue (if applicable) |
| Credit bureau data | CBC | Existing obligations |
| RM notes | CRM / Manual | Field observations, farmer contact |
| Farm GPS/polygon | Mobile app / RM | Farm location (collected during pilot) |

### Free API URLs & Setup Guide

All external data sources listed above are **free of charge**. Below are the exact URLs, GEE collection IDs, and setup instructions for each.

#### 1. Sentinel-2 Optical Imagery (ESA / Copernicus)

| Item | Detail |
|------|--------|
| **Provider** | European Space Agency (ESA) via Copernicus Programme |
| **Cost** | **Free** — open data policy, no restrictions on commercial/non-commercial use |
| **GEE Collection ID** | `COPERNICUS/S2_SR_HARMONIZED` |
| **Direct Download** | https://dataspace.copernicus.eu/ |
| **GEE Browser** | https://code.earthengine.google.com/ |
| **Copernicus Browser** | https://browser.dataspace.copernicus.eu/ |
| **Documentation** | https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_SR_HARMONIZED |
| **Coverage** | Global (56°S to 83°N). **Cambodia (103°-108°E, 10°-15°N) fully covered** |
| **Resolution** | 10m (B2-B4, B8), 20m (B5-B7, B8A, B11-B12) |
| **Revisit** | Every 5 days (2 satellites: S2A + S2B) |
| **Bands for NDVI** | B4 (Red, 665nm) + B8 (NIR, 842nm) |
| **Bands for NDWI** | B3 (Green, 560nm) + B8 (NIR, 842nm) |
| **Bands for EVI** | B2 (Blue) + B4 (Red) + B8 (NIR) |
| **Cloud masking** | SCL band (Scene Classification) — values 8,9,10 = cloud |
| **Setup** | 1. Sign up at https://earthengine.google.com/ (free for research/non-commercial) 2. Create GCP project at https://console.cloud.google.com/ 3. Enable Earth Engine API 4. Run `earthengine authenticate` |
| **Env var** | `GEE_PROJECT_ID=your-project-id` |
| **Proof for Cambodia** | FAO has demonstrated AI rice-field mapping using Sentinel-2 in Cambodia (https://www.fao.org/cambodia/news/detail/geo-ai-for-agriculture-workshop-in-cambodia/en) |

**Verify Cambodia coverage now:**
```javascript
// Paste in GEE Code Editor: https://code.earthengine.google.com/
Map.setCenter(104.9, 12.5, 7); // Cambodia center
var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterDate('2026-06-01', '2026-09-01')
  .filterBounds(ee.Geometry.Rectangle([102, 10, 108, 15]))
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
  .median();
Map.addLayer(s2, {bands: ['B4','B3','B2'], min: 0, max: 3000});
```

---

#### 2. Sentinel-1 SAR Imagery (ESA / Copernicus)

| Item | Detail |
|------|--------|
| **Provider** | ESA via Copernicus |
| **Cost** | **Free** |
| **GEE Collection ID** | `COPERNICUS/S1_GRD` |
| **Direct Download** | https://dataspace.copernicus.eu/ |
| **Documentation** | https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD |
| **Coverage** | Global. **Cambodia fully covered** |
| **Resolution** | 10m |
| **Revisit** | Every 6-12 days |
| **Polarizations** | VV (surface scattering), VH (volume scattering) |
| **Key advantage** | **Penetrates clouds** — critical for Cambodia's wet season (May-Oct) |
| **Use case** | Flood detection, soil moisture, crop structure |
| **Setup** | Same GEE account as Sentinel-2 |
| **Env var** | `GEE_PROJECT_ID=your-project-id` |

**Verify:**
```javascript
var s1 = ee.ImageCollection('COPERNICUS/S1_GRD')
  .filterBounds(ee.Geometry.Rectangle([102, 10, 108, 15]))
  .filterDate('2026-06-01', '2026-09-01')
  .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
  .select('VV');
Map.addLayer(s1, {min: -25, max: 0});
```

---

#### 3. CHIRPS Rainfall (UCSB / Climate Hazards Center)

| Item | Detail |
|------|--------|
| **Provider** | UC Santa Barbara Climate Hazards Center |
| **Cost** | **Free** |
| **Website** | https://data.chc.ucsb.edu/products/CHIRPS-2.0/ |
| **Documentation** | https://www.chc.ucsb.edu/data/chirps |
| **Coverage** | Global land areas (50°S to 50°N). **Cambodia fully covered** |
| **Resolution** | 0.05° (~5.5 km) |
| **Temporal** | Daily, pentadal (5-day), monthly |
| **Format** | GeoTIFF, NetCDF |
| **API** | Direct file access (no auth needed) |
| **URL pattern** | `https://data.chc.ucsb.edu/products/CHIRPS-2.0/daily/p05/{YYYY}/chirps-v2.0.{YYYY}.{MM}.{DD}.tif` |
| **Env var** | `CHIRPS_API_URL=https://data.chc.ucsb.edu/products/CHIRPS-2.0` |
| **Note** | Originally developed for drought monitoring in Africa and Asia |

---

#### 4. ERA5 Temperature (ECMWF)

| Item | Detail |
|------|--------|
| **Provider** | European Centre for Medium-Range Weather Forecasts (ECMWF) |
| **Cost** | **Free** (requires registration) |
| **Website** | https://cds.climate.copernicus.eu/ |
| **CDS API** | https://cds.climate.copernicus.eu/api |
| **Documentation** | https://cds.climate.copernicus.eu/how-to-api |
| **Coverage** | **Global** (every 0.25° grid cell on Earth) |
| **Resolution** | 0.25° (~25 km) |
| **Temporal** | Hourly (aggregated to daily/monthly) |
| **Variables** | 2m temperature, precipitation, wind, humidity |
| **Setup** | 1. Register at https://cds.climate.copernicus.eu/ (free) 2. Go to "API key" page 3. Copy UID + API key 4. Set `ERA5_API_URL` and `ERA5_API_KEY` |
| **Env vars** | `ERA5_API_URL=https://cds.climate.copernicus.eu/api` / `ERA5_API_KEY=UID:API_KEY` |

---

#### 5. MODIS Land Cover (NASA)

| Item | Detail |
|------|--------|
| **Provider** | NASA via GEE |
| **Cost** | **Free** |
| **GEE Collection ID** | `MODIS/061/MCD12Q1` |
| **Documentation** | https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD12Q1 |
| **Coverage** | **Global** |
| **Resolution** | 500m |
| **Temporal** | Annual (16-day composites) |
| **Use case** | Identify croplands vs. forest vs. urban. IGBP classification |
| **Key class for SARP** | Class 12 (croplands), Class 14 (cropland/natural mosaic) |
| **Setup** | Same GEE account as Sentinel-2 |
| **Env var** | `GEE_PROJECT_ID=your-project-id` |

---

#### 6. Cambodia Admin Boundaries (GADM)

| Item | Detail |
|------|--------|
| **Provider** | Database of Global Administrative Areas (GADM) |
| **Cost** | **Free** for non-commercial use |
| **Website** | https://gadm.org/download_country.html |
| **Cambodia download** | https://gadm.org/download_country.html → Select "Cambodia" → Shapefile/GeoJSON |
| **Coverage** | All 25 Cambodian provinces, 202 districts |
| **Format** | Shapefile, GeoJSON, GeoPackage |
| **Levels** | Level 0 (country), Level 1 (province), Level 2 (district), Level 3 (commune) |
| **Setup** | Download once, extract to `backend/data/gadm41_KHM_shp/` |
| **Env var** | None (local file) |

**Cambodian provinces (25):**
| Code | Province | Code | Province |
|------|----------|------|----------|
| 01 | Phnom Penh | 14 | Preah Vihear |
| 02 | Banteay Meanchey | 15 | Pursat |
| 03 | Battambang | 16 | Ratanak Kiri |
| 04 | Kampong Cham | 17 | Siem Reap |
| 05 | Kampong Chhnang | 18 | Sihanoukville |
| 06 | Kampong Speu | 19 | Stung Treng |
| 07 | Kampong Thom | 20 | Svay Rieng |
| 08 | Kampot | 21 | Takeo |
| 09 | Kandal | 22 | Oddar Meanchey |
| 10 | Koh Kong | 23 | Tboung Khmum |
| 11 | Kratie | 24 | Pailin |
| 12 | Mondulkiri | 25 | Prey Veng |
| 13 | Phnom Penh | | |

---

#### 7. MRC Flood Data (Mekong River Commission)

| Item | Detail |
|------|--------|
| **Provider** | Mekong River Commission |
| **Cost** | **Free** |
| **Portal** | https://portal.mrcmekong.org/ |
| **Flood Monitoring** | https://portal.mrcmekong.org/flood-monitoring |
| **API** | https://portal.mrcmekong.org/api (registration required) |
| **Coverage** | Mekong Basin: **Cambodia, Laos, Thailand, Vietnam** |
| **Cambodia relevance** | Mekong River, Tonle Sap Lake, Bassac River — all major Cambodia water systems |
| **Data types** | Water levels, flood alerts, rainfall, flow forecasts |
| **Update** | Near-real-time (hourly to daily) |
| **Setup** | Register at https://portal.mrcmekong.org/ |
| **Env var** | `MRC_API_URL=https://portal.mrcmekong.org/api` |

---

#### 8. Google Earth Engine (GEE) — Central Access Point

| Item | Detail |
|------|--------|
| **What** | Cloud-based geospatial analysis platform |
| **Cost** | **Free** for research, non-commercial, and education |
| **Website** | https://earthengine.google.com/ |
| **Code Editor** | https://code.earthengine.google.com/ |
| **Python API** | `pip install earthengine-api` |
| **JavaScript API** | Built into Code Editor |
| **Data available** | Sentinel-1, Sentinel-2, MODIS, Landsat, ERA5, CHIRPS, and 40+ petabytes of Earth observation data |
| **Advantage** | No need to download satellite data — process in the cloud |
| **Setup steps** | 1. Sign up at https://earthengine.google.com/ (approval usually instant for .edu/org emails) 2. Create GCP project at https://console.cloud.google.com/ 3. Enable Earth Engine API 4. Authenticate: `earthengine authenticate` 5. Set `GEE_PROJECT_ID` env var |
| **Cambodia coverage** | Full. All Sentinel/MODIS/Landsat data covers Cambodia |

---

#### 9. Additional Free Data Sources

| Data Source | Provider | URL | Purpose |
|-------------|----------|-----|---------|
| Landsat 8/9 | NASA/USGS | https://landsat.gsfc.nasa.gov/ (or GEE: `LANDSAT/LC08/C02/T1_L2`) | 30m optical, historical baselines |
| CHIRPS Pentadal | UCSB | https://data.chc.ucsb.edu/products/CHIRPS-2.0/pentadal/ | 5-day rainfall aggregates |
| CHIRPS Monthly | UCSB | https://data.chc.ucsb.edu/products/CHIRPS-2.0/monthly/ | Monthly rainfall totals |
| OpenStreetMap | OSM Foundation | https://www.openstreetmap.org/ | Road networks, village boundaries |
| Cambodia HIES | NIS Cambodia | https://www.nis.gov.kh/ | Household income/expenditure survey |
| WorldPop | UMAP | https://www.worldpop.org/ | Population density grids |
| Soil Grids | ISRIC | https://soilgrids.org/ | Global soil properties |
| Crop Calendar | FAO | https://www.fao.org/giews/countrybrief/country.jsp?KHM | Cambodia crop calendar |

---

### Data integration approach

```
┌─────────────────┐     ┌──────────────────┐
│ External Data   │     │ Internal Data    │
│ (Satellite,     │     │ (CBS, Loan,      │
│  Weather, GIS)  │     │  Payments, CRM)  │
└────────┬────────┘     └────────┬─────────┘
         │                       │
         ▼                       ▼
┌─────────────────────────────────────────┐
│         DATA LAKE / WAREHOUSE           │
│                                         │
│  • Raw satellite scenes                 │
│  • Processed spectral indices           │
│  • Weather summaries                    │
│  • Farm polygons                        │
│  • Farmer/loan records                  │
│  • Transaction features                 │
│  • Risk scores                          │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│         FEATURE STORE                   │
│                                         │
│  Per-farm, per-period features          │
│  Ready for model training/inference     │
└────────────────────┬────────────────────┘
                     │
              ┌──────┴──────┐
              ▼             ▼
         ┌─────────┐  ┌──────────┐
         │ Training│  │ Inference│
         │ Pipeline│  │ Pipeline │
         └─────────┘  └──────────┘
```

---

## 7. Technical Architecture

### High-level architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                       │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│  │ Farm Monitor │  │ Risk Dashboard│ │ Alert / Workflow │    │
│  │ (GIS View)   │  │ (Portfolio)   │ │ (RM Actions)     │    │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘    │
└─────────┼──────────────────┼───────────────────┼─────────────┘
          │                  │                   │
          ▼                  ▼                   ▼
┌──────────────────────────────────────────────────────────────┐
│                     API / SERVICE LAYER                      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│  │ Farm Service │  │ Risk Service │  │ Alert Service    │    │
│  │              │  │              │  │                  │    │
│  │ CRUD farm    │  │ Score calc   │  │ Threshold engine │    │
│  │ profiles     │  │ Model serve  │  │ RM notification  │    │
│  │ Polygon mgmt │  │ Explainability│ │ Workflow triggers│    │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘    │
└─────────┼──────────────────┼───────────────────┼─────────────┘
          │                  │                   │
          ▼                  ▼                   ▼
┌──────────────────────────────────────────────────────────────┐
│                     PROCESSING LAYER                         │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│  │ Satellite    │  │ Weather      │  │ Feature          │    │
│  │ Ingestion    │  │ Ingestion    │  │ Engineering      │    │
│  │              │  │              │  │                  │    │
│  │ Sentinel-2   │  │ CHIRPS       │  │ Per-farm stats   │    │
│  │ Sentinel-1   │  │ ERA5         │  │ Time-series      │    │
│  │ Cloud mask   │  │ MRC flood    │  │ Deviation calc   │    │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘    │
└─────────┼──────────────────┼───────────────────┼─────────────┘
          │                  │                   │
          ▼                  ▼                   ▼
┌──────────────────────────────────────────────────────────────┐
│                     DATA LAYER                               │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Object Store  │  │ Database      │  │ Feature Store     │  │
│  │               │  │               │  │                    │  │
│  │ GeoTIFF       │  │ PostgreSQL    │  │ Farm features      │  │
│  │ Sentinel scenes│ │ + PostGIS     │  │ Risk features      │  │
│  │ Processed rasters│              │  │ Time-series        │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### Technology stack (PoC recommendation)

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Satellite data access | Google Earth Engine (GEE) API or SentinelsHub | Free tier, pre-processed Sentinel data, cloud-free composites |
| GIS processing | Python + rasterio + geopandas + shapely | Standard geospatial stack, well-documented |
| Feature engineering | Python + pandas + numpy | Time-series feature calculation |
| ML/Model training | Python + scikit-learn + XGBoost | Interpretable, fast, sufficient for PoC |
| Model serving | FastAPI + Docker | Lightweight, easy to deploy |
| Database | PostgreSQL + PostGIS | Spatial queries, farm records |
| Feature store | SQLite / Parquet files (PoC) | Simple, no infra overhead |
| Dashboard | Streamlit or React + Leaflet | Rapid prototyping (Streamlit) or production (React) |
| Scheduling | Apache Airflow or cron | Orchestrate satellite ingestion, scoring |
| Cloud | AWS or GCP | Compute, storage, managed services |

### Deployment model (PoC)

**Minimal infrastructure:**

- 1x cloud VM (8 vCPU, 32GB RAM) for processing 
- 1x cloud VM (4 vCPU, 16GB RAM) for dashboard
- 1x PostgreSQL instance
- 1x object storage bucket
- GEE account (free tier)

**Estimated monthly cloud cost (PoC):** $300–600

---

## 8. Farm Mapping — Stage 1

### Objective

Create a digital farm profile for each pilot borrower by:
1. Collecting GPS coordinates
2. Detecting farm boundaries from satellite imagery
3. Classifying the crop type
4. Validating area against loan records

### Data collection process

```
Loan Officer / RM
        │
        ▼
Mobile App (or GPS device)
        │
        ├── Farmer ID
        ├── GPS points (boundary walk)
        ├── Crop type (farmer input)
        └── Photos (optional)
                │
                ▼
        Farm Mapping Service
                │
                ▼
        Digital Farm Profile
```

### Boundary detection approach

**Option A: Manual GPS collection (primary for PoC)**

- RM walks the farm boundary with a GPS device or mobile app
- Points are converted to a polygon
- This is the most reliable method for the PoC

**Option B: Satellite-based segmentation (validation/future)**

- Use Sentinel-2 + semantic segmentation model
- Identify crop parcels automatically
- Validated by FAO in Cambodia for rice fields
- Useful as a cross-check against GPS data

### Farm profile schema

```json
{
  "farm_id": "FARM-001",
  "farmer_id": "F001",
  "loan_id": "AGR-2026-001",
  "location": {
    "province": "Battambang",
    "district": "Battambang",
    "commune": "Svay Pao",
    "centroid_lat": 13.1234,
    "centroid_lon": 103.2345
  },
  "boundary": {
    "type": "Polygon",
    "coordinates": [[[...], ...]],
    "crs": "EPSG:4326"
  },
  "area_hectares": {
    "gps_measured": 5.2,
    "satellite_detected": 4.9,
    "loan_record": 5.0
  },
  "crop": {
    "type": "rice",
    "variety": "unknown",
    "planting_date": "2026-06-15",
    "expected_harvest": "2026-10-30",
    "season": "wet"
  },
  "mapping": {
    "boundary_source": "gps",
    "boundary_confidence": 0.97,
    "crop_classification_confidence": 0.94,
    "mapped_date": "2026-07-01",
    "validated_by": "RM-042"
  }
}
```

### Success metrics — Stage 1

| KPI | Target | Measurement |
|-----|--------|-------------|
| Farm successfully mapped | ≥90% | Farms with valid polygon / total pilot farms |
| Boundary IoU (GPS vs. satellite) | ≥85% | Intersection over Union |
| Area estimation error | ≤10% | |GPS area - satellite area| / GPS area |
| Crop classification accuracy | ≥90% | Correct crop type / total classified |
| Farmer-farm linkage accuracy | ≥100% | Verified via RM validation |
| Processing time per farm | <5 min | Automated pipeline runtime |

---

## 9. Crop Health Monitoring — Stage 2

### Objective

Establish a per-farm, time-series crop health monitoring pipeline that:
1. Ingests satellite imagery periodically
2. Calculates vegetation and moisture indices
3. Detects deviations from normal crop growth
4. Generates a Crop Health Score

### Satellite data pipeline

```
Sentinel-2 (optical)
        │
        ▼
Cloud masking (SCL band or s2cloudless)
        │
        ▼
Surface reflectance
        │
        ▼
Spectral indices per farm
        │
        ├── NDVI = (NIR - Red) / (NIR + Red)
        ├── NDWI = (Green - NIR) / (Green + NIR)
        ├── EVI = 2.5 * (NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1)
        └── Red Edge indices (if available)
        │
        ▼
Zonal statistics per farm polygon
        │
        ├── Mean, median, std dev
        ├── Percentiles (10th, 25th, 75th, 90th)
        └── Fraction of area above/below thresholds
        │
        ▼
Time-series record
```

```
Sentinel-1 (SAR)
        │
        ▼
Pre-processing (orbit, calibration, speckle filter)
        │
        ▼
VV and VH backscatter
        │
        ▼
Zonal statistics per farm polygon
        │
        ├── Mean VV, VH
        └── VH/VV ratio
        │
        ▼
Flood/moisture indicators
```

### Cloud cover handling

Cambodia has significant cloud cover during wet season (May–October).

Strategies:

1. **Cloud masking** — remove cloudy pixels using SCL band or cloud probability
2. **Compositing** — build weekly/monthly cloud-free composites
3. **SAR fallback** — Sentinel-1 radar works through clouds
4. **Temporal interpolation** — fill gaps using surrounding clear observations
5. **Accept reduced coverage** — target ≥80% usable observations per farm per month

### Crop health indices

#### NDVI time-series

```
NDVI

1.0 |                  /\
    |                /    \
0.8 |             __/      \__
    |          __/
0.6 |       __/
    |    __/
0.4 |___/
    +---------------------------->
       Planting       Growth  Harvest
```

The model establishes a **normal crop-growth curve** for each crop type in each region.

**Deviation from the curve** becomes the primary signal.

#### Growth stage classification

| Stage | Typical NDVI (rice) | Description |
|-------|---------------------|-------------|
| Bare soil / pre-planting | 0.2–0.3 | No vegetation |
| Early vegetative | 0.3–0.5 | Seedling establishment |
| Active vegetative | 0.5–0.7 | Rapid growth |
| Reproductive | 0.7–0.85 | Panicle development |
| Maturity | 0.6–0.75 | Grain filling, senescence |
| Harvest / post-harvest | 0.2–0.4 | Residue, bare soil |

### Crop Health Score

Composite score combining multiple indicators:

| Component | Weight | Data Source |
|-----------|--------|-------------|
| NDVI deviation from normal | 30% | Sentinel-2 |
| NDVI trend (declining?) | 20% | Sentinel-2 time-series |
| NDWI (moisture status) | 15% | Sentinel-2 |
| SAR moisture signal | 10% | Sentinel-1 |
| Rainfall deviation | 15% | CHIRPS |
| Temperature stress | 10% | ERA5 |

#### Score scale

| Score Range | Status | Color | Meaning |
|-------------|--------|-------|---------|
| 80–100 | Normal | 🟢 Green | Crop developing normally |
| 60–79 | Mild Stress | 🟡 Yellow | Some deviation, monitor closely |
| 40–59 | Significant Stress | 🟠 Orange | Clear deterioration, investigate |
| <40 | Severe Stress | 🔴 Red | Major crop health issue detected |

**Note:** Thresholds will be calibrated during the PoC against field observations. Initial thresholds are starting points only.

### Example farm output

```
Farm: FARM-001
Date: 2026-09-15

Crop: Rice
Growth stage: Reproductive
Farm area: 4.9 hectares

Vegetation indices:
  NDVI (current):    0.52
  NDVI (historical): 0.74
  NDVI deviation:    -29.7%
  NDVI trend:        Declining (3 consecutive observations)
  NDWI:              0.18 (low moisture)

Weather:
  Rainfall (30-day): 62mm (normal: 145mm, -57%)
  Temperature:       Normal
  Drought risk:      High

SAR:
  VH backscatter:    Declining
  Flood risk:        Low

Crop Health Score: 38/100
Status: 🔴 RED — Severe Stress

Confidence: 87%
Last observation: 2026-09-12
```

### Success metrics — Stage 2

| KPI | Target | Measurement |
|-----|--------|-------------|
| Farm monitoring coverage | ≥90% | Farms with ≥3 observations/month |
| Cloud-free usable observations | ≥80% | Of expected observations |
| Crop health classification accuracy | ≥80–85% | Validated against RM observations |
| Flood detection accuracy | ≥85% | vs. MRC flood reports |
| Significant stress detection recall | ≥80% | Correctly flagged / actual stress events |
| False alert rate | <15–20% | False alerts / total alerts |
| Alert lead time | ≥2–4 weeks | Time before observed financial stress |

---

## 10. Credit Early Warning — Stage 3

### Objective

Combine satellite-derived crop health signals with Sathapana's financial data to produce a **Probability of Repayment Difficulty** for each agricultural borrower.

### Feature categories

#### Satellite / environmental features

| Feature | Description |
|---------|-------------|
| ndvi_current | Current NDVI value |
| ndvi_deviation_pct | % deviation from historical normal |
| ndvi_trend_3obs | NDVI trend over last 3 observations |
| ndvi_trend_5obs | NDVI trend over last 5 observations |
| ndwi_current | Current NDWI value |
| crop_health_score | Composite score from Stage 2 |
| growth_stage | Current growth stage (encoded) |
| flood_exposure | Binary: farm in flood-affected area |
| drought_stress | Derived from NDVI decline + low rainfall |
| rainfall_deviation_30d | 30-day rainfall vs. normal |
| rainfall_deviation_60d | 60-day rainfall vs. normal |
| temperature_stress_days | Days with extreme temperature |
| days_since_last_clear_obs | Data freshness |

#### Farm / agricultural features

| Feature | Description |
|---------|-------------|
| farm_area_hectares | Validated farm area |
| crop_type | Rice (encoded) |
| planting_date | Day of year |
| days_since_planting | Crop age |
| expected_harvest_date | Days until harvest |
| is_wet_season | Season indicator |
| province_risk_factor | Historical crop failure rate by province |

#### Financial / banking features

| Feature | Description |
|---------|-------------|
| loan_outstanding | Current outstanding principal |
| installment_amount | Monthly installment |
| dpd | Days past due (current) |
| dpd_max_90d | Maximum DPD in last 90 days |
| missed_payments_count | Number of missed payments |
| restructured | Whether loan was restructured |
| deposit_balance_trend_30d | 30-day change in average balance |
| deposit_balance_trend_60d | 60-day change |
| transaction_count_30d | Number of transactions in 30 days |
| cash_inflow_30d_60d_ratio | Recent vs. prior month inflow |
| cash_outflow_30d_60d_ratio | Recent vs. prior month outflow |
| agricultural_income_detected | Whether agri-related transactions detected |
| days_since_last_deposit | Recency of account activity |
| balance_to_installment_ratio | Available balance / next installment |
| external_obligations | Credit bureau data (if available) |

#### Temporal / behavioral features

| Feature | Description |
|---------|-------------|
| repayment_consistency_score | Historical payment pattern |
| seasonal_cash_flow_pattern | Typical seasonality |
| deviation_from_normal_behavior | Anomaly in transaction patterns |

### Target variable

**Not "default"** — too rare, too late.

Define target as:

```
Y = 1 if borrower experiences any of:
    - DPD ≥ 30 within next 90 days
    - Restructuring request within next 90 days
    - Account balance drops below 50% of installment for 30+ days
    
Y = 0 otherwise
```

Use a **90-day forward-looking window** from each observation point.

### Model design

#### Phase 1: Baseline models

| Model | Purpose | Rationale |
|-------|---------|-----------|
| Logistic Regression | Interpretable baseline | Easy to explain to management |
| XGBoost | Performance baseline | Handles non-linearity, feature interactions |

#### Feature importance / explainability

Use SHAP values to show **why** each farmer is flagged:

```
Farmer F001 — Risk Score: 82%

Top contributing factors:
  1. NDVI deviation -31%        (+18% risk)
  2. Rainfall deviation -42%    (+14% risk)
  3. Deposit inflow -26%        (+12% risk)
  4. Crop health score: 38      (+10% risk)
  5. Days since last deposit: 28 (+5% risk)

Protective factors:
  - No previous missed payments  (-3% risk)
  - Farm size above average      (-2% risk)
```

### Model outputs

```json
{
  "farmer_id": "F001",
  "loan_id": "AGR-2026-001",
  "farm_id": "FARM-001",
  "scoring_date": "2026-09-15",
  "risk_score": 0.82,
  "risk_bucket": "RED",
  "confidence": 0.87,
  "primary_drivers": [
    {"feature": "ndvi_deviation_pct", "value": -31, "contribution": 0.18},
    {"feature": "rainfall_deviation_30d", "value": -42, "contribution": 0.14},
    {"feature": "cash_inflow_30d_60d_ratio", "value": 0.74, "contribution": 0.12}
  ],
  "recommended_action": "RM_REVIEW",
  "alert_generated": true,
  "alert_id": "ALT-2026-00142"
}
```

### Risk buckets

| Score Range | Bucket | Color | Action |
|-------------|--------|-------|--------|
| 0.00–0.30 | GREEN | 🟢 | Normal monitoring |
| 0.31–0.55 | AMBER | 🟡 | Enhanced monitoring, RM awareness |
| 0.56–0.75 | ORANGE | 🟠 | RM contact, risk review |
| 0.76–1.00 | RED | 🔴 | Urgent RM intervention, possible restructuring |

### Success metrics — Stage 3

| KPI | Target | Measurement |
|-----|--------|-------------|
| Risk model AUC | ≥0.75 | Cross-validated |
| High-risk borrowers detected (recall) | ≥70–80% | Of actual stressed borrowers |
| False-positive rate | <20% | False alarms / total alerts |
| Early-warning lead time | ≥30 days | Days before delinquency observed |
| RM adoption rate | ≥80% | RMs actively using dashboard |
| Alert investigation rate | ≥70% | Alerts reviewed by RM within 7 days |

---

## 11. Risk Model Design

### Training approach

```
Historical Data (if available)
        │
        ▼
Feature Engineering
        │
        ▼
Train/Validation/Test Split
        │ (temporal split, not random)
        ├── Train: Months 1–N-3
        ├── Validation: Months N-2 to N-1
        └── Test: Month N
        │
        ▼
Model Training
        │
        ├── Logistic Regression
        └── XGBoost
        │
        ▼
Hyperparameter Tuning (validation set)
        │
        ▼
Final Evaluation (test set)
        │
        ▼
Threshold Selection (business-driven)
```

### Why temporal split?

Random train/test split would leak future information into training. Agricultural and financial data are inherently time-dependent.

### Cold-start problem

At PoC start, there may not be enough historical data to train a model. Solutions:

1. **Back-test** using historical satellite data + historical loan performance
2. **Transfer learning** from published agricultural credit models
3. **Start with rule-based scoring** and transition to ML once sufficient data accumulates
4. **Use satellite features alone** in a simpler model as the initial baseline

### Model monitoring

After deployment, continuously monitor:

- Score distribution drift
- Feature drift
- Prediction calibration
- Actual vs. predicted default rates
- False-positive / false-negative rates

---

## 12. Dashboard & Alert System

### Dashboard views

#### 1. Portfolio overview

```
╔════════════════════════════════════════════╗
║       AGRICULTURAL CREDIT MONITOR          ║
╠════════════════════════════════════════════╣
║                                            ║
║  Agricultural Portfolio                    ║
║                                            ║
║  2,450 Farmers                             ║
║  $18.4M Outstanding                        ║
║                                            ║
║  🟢 Normal       1,920                     ║
║  🟡 Watch          390                     ║
║  🟠 High Risk      105                     ║
║  🔴 Critical        35                     ║
║                                            ║
╠════════════════════════════════════════════╣
║ PROVINCE BREAKDOWN                         ║
║                                            ║
║ Battambang    🟢 680  🟡 95  🟠 30  🔴 12 ║
║ Siem Reap     🟢 540  🟡 78  🟠 22  🔴  8 ║
║ Kampong Cham  🟢 700  🟡 217 🟠 53  🔴 15 ║
╚════════════════════════════════════════════╝
```

#### 2. Early-warning list

```
╔════════════════════════════════════════════╗
║ TOP EARLY-WARNING BORROWERS                ║
╠════════════════════════════════════════════╣
║                                            ║
║ F001   82% 🔴   Crop stress + cashflow    ║
║ F087   76% 🔴   Flood exposure            ║
║ F123   69% 🟠   NDVI deterioration        ║
║ F341   63% 🟠   Drought + low deposits    ║
║ F567   58% 🟠   Rainfall deficit          ║
║ F890   55% 🟡   Declining NDVI            ║
╚════════════════════════════════════════════╝
```

#### 3. Individual farmer detail

```
F001 — Agricultural Loan

Loan Outstanding: $7,850
Monthly Installment: $875
DPD: 0 (current)

Crop: Rice
Farm: 4.9 hectares, Battambang

Crop Health          🔴 38
Weather Risk         🔴 High
Cash Flow Trend      🟠 Declining
Repayment Behaviour  🟢 Good

PD / Stress Risk: 82%

NDVI time-series: [chart]

Primary drivers:
  1. NDVI -31%
  2. Rainfall -42%
  3. Deposit inflow -26%
  4. Crop failure probability elevated

RM: Sovannara (RM-042)
Last contact: 2026-08-20

Recommended action:
  → RM to contact farmer
  → Assess crop situation
  → Consider restructuring options
  → Evaluate crop insurance eligibility
```

#### 4. Farm map view

Interactive map showing:
- Farm boundaries (color-coded by risk)
- Flood extent overlay
- Satellite imagery basemap
- Click-to-detail

### Alert workflow

```
Risk score crosses threshold
        │
        ▼
Alert generated
        │
        ├── Alert ID
        ├── Farmer details
        ├── Risk score + drivers
        └── Recommended action
        │
        ▼
Notification sent
        │
        ├── Email to RM
        ├── In-app notification
        └── Daily digest (batch)
        │
        ▼
RM reviews alert
        │
        ├── Investigate (contact farmer, check records)
        ├── Dismiss (with reason)
        └── Escalate (to credit risk)
        │
        ▼
Action taken
        │
        ├── No action needed
        ├── Farmer contacted
        ├── Restructuring initiated
        ├── Insurance claim
        └── Escalated to NPL team
        │
        ▼
Outcome recorded
        │
        ▼
Fed back to model (learning loop)
```

---

## 13. Pilot Design — Control Group

### Why a control group?

Without a control group, you cannot answer the executive question:

> *"Did this actually improve Sathapana's credit outcomes?"*

You can only answer:

> *"Does the AI model produce scores?"*

The control group makes the PoC a **business experiment**, not just a technology demo.

### Design

```
1,000 Agricultural Borrowers (pilot provinces)

        │
        ┌───────────────┐
        │               │
        ▼               ▼
   700 Pilot         300 Control
   Group             Group
        │               │
        ▼               ▼
AI Early Warning    Existing Process
Dashboard + Alerts  (no AI monitoring)
        │               │
        ▼               ▼
RM takes action     RM follows normal
based on AI alerts  procedures
        │               │
        └───────┬───────┘
                ▼
          Compare after
          pilot period
```

### Randomization

- Randomly assign farmers to pilot vs. control
- Stratify by province, loan size, crop type to ensure balance
- RMs should not know which farmers are in which group (if feasible)
- **Important:** Control group farmers still receive normal service — they are NOT disadvantaged

### Measurement

| Metric | Pilot Group | Control Group | Comparison |
|--------|------------|---------------|------------|
| DPD ≥ 30 rate | ? | ? | Difference |
| DPD ≥ 60 rate | ? | ? | Difference |
| NPL migration rate | ? | ? | Difference |
| Restructuring rate | ? | ? | Difference |
| Recovery rate | ? | ? | Difference |
| Average days to RM intervention | ? | ? | Difference |
| Loss rate | ? | ? | Difference |

### Statistical significance

With 700/300 split and assuming:
- Base delinquency rate: ~5–10%
- Minimum detectable effect: 20–30% relative reduction
- Significance level: 0.05
- Power: 0.80

This sample size should be sufficient to detect meaningful differences.

### Ethical note

If the AI system identifies a farmer as genuinely at risk, it would be unethical to withhold that information from the control group in a real production environment. For the PoC, the control group simply operates under the existing process. Any farmer in the control group who becomes delinquent would still receive normal collections support.

---

## 14. Success Metrics & KPIs

### Technical KPIs

| KPI | Stage | Target | Measurement Method |
|-----|-------|--------|--------------------|
| Farm mapping success rate | 1 | ≥90% | Farms with valid polygon / total |
| Boundary accuracy (IoU) | 1 | ≥85% | GPS vs. satellite boundary overlap |
| Area estimation error | 1 | ≤10% | |GPS - satellite| / GPS |
| Crop classification accuracy | 1 | ≥90% | Correct / total classified |
| Observation completeness | 2 | ≥80% | Usable obs / expected obs |
| Crop health classification | 2 | ≥80–85% | vs. RM field validation |
| Flood detection accuracy | 2 | ≥85% | vs. MRC flood reports |
| Stress detection recall | 2 | ≥80% | Correctly flagged / actual events |
| False alert rate | 2–3 | <20% | False / total alerts |
| Risk model AUC | 3 | ≥0.75 | Cross-validated |
| Alert lead time | 3 | ≥30 days | Days before financial stress |

### Business KPIs

| KPI | Target | Measurement |
|-----|--------|-------------|
| High-risk borrowers detected before delinquency | ≥70–80% | Of actual stressed borrowers |
| False-positive rate | <20% | False alerts / total alerts |
| Reduction in unexpected delinquency | 10–20%* | Pilot vs. control |
| RM investigation time reduction | -30% | Average time to first contact |
| RM dashboard adoption | ≥80% | RMs actively using daily |
| Alert investigation rate | ≥70% | Alerts reviewed within 7 days |
| NPL migration reduction | Measurable | Pilot vs. control |

*The 10–20% figure is a hypothesis/target, not an assumed outcome. Must be validated against control group.*

### Overall PoC success criteria

The PoC is considered **successful** if:

1. ✅ ≥85% of technical KPIs are met
2. ✅ Risk model AUC ≥ 0.75
3. ✅ Alert lead time ≥ 30 days
4. ✅ ≥70% of high-risk borrowers detected before delinquency
5. ✅ RM team actively uses the dashboard (≥80% adoption)
6. ✅ Control group comparison shows measurable improvement (or strong signal thereof)
7. ✅ Management sees a credible path to scale

---

## 15. Implementation Plan — 16 Weeks

### Gantt overview

```
Week  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16
      │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │
S1    │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│                          Farm Mapping
S2    │         │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│               Crop Health
S3    │                  │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│    Credit Warning
      │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │
```

### Detailed week-by-week plan

| Week | Activity | Owner | Deliverable |
|------|----------|-------|-------------|
| **1** | Select pilot portfolio (500–1,000 borrowers in 1–2 provinces) | Credit Risk + Data | Borrower list with loan records |
| **1** | Define KPIs, success criteria, control group design | Project Lead | KPI document, approved by management |
| **2** | Procure/set up cloud infrastructure | Data Engineering | Working dev environment |
| **2** | Begin GPS data collection for farm boundaries | RMs / Field Officers | Mobile app deployed, collection started |
| **3** | Set up satellite data ingestion pipeline (Sentinel-2, Sentinel-1) | Data Engineering | Automated data pull working |
| **3–4** | Collect GPS data for ≥80% of pilot farms | RMs / Field Officers | Farm polygons in database |
| **4** | Set up weather data ingestion (CHIRPS, ERA5) | Data Engineering | Weather data flowing |
| **4–5** | Build farm mapping validation pipeline | ML Engineer | Farm profiles created |
| **5–6** | Develop satellite preprocessing pipeline (cloud masking, compositing) | Data Engineering | Clean satellite time-series |
| **6** | Build spectral index calculation pipeline (NDVI, NDWI, EVI) | ML Engineer | Index values per farm per date |
| **6–7** | Validate farm mapping against GPS and loan records | Data Analyst | Stage 1 validation report |
| **7** | Build crop-growth curve model for rice | ML Engineer | Normal growth curves by province |
| **7–8** | Set up weather/flood risk integration | Data Engineering | Environmental risk signals |
| **8** | Build Crop Health Score calculation | ML Engineer | Health scores per farm |
| **8–9** | Develop feature engineering pipeline for credit risk model | Data Engineer | Feature store populated |
| **9** | Collect RM field observations for model validation labels | RMs | Labeled dataset (sample) |
| **10** | Train baseline credit risk models (Logistic Reg + XGBoost) | ML Engineer | Trained models, AUC reported |
| **10–11** | Build crop health time-series dashboard | Frontend Engineer | Dashboard v1 deployed |
| **11** | Integrate Sathapana financial data into feature pipeline | Data Engineering | Financial features available |
| **11–12** | Build risk scoring pipeline | ML Engineer | End-to-end scoring working |
| **12** | Calibrate risk thresholds with business stakeholders | Credit Risk + ML | Thresholds approved |
| **12–13** | Build alert workflow and notification system | Backend Engineer | Alerts triggering correctly |
| **13** | Build early-warning dashboard | Frontend Engineer | Dashboard v2 with alerts |
| **13–14** | RM training and onboarding | Project Lead + RM Lead | RMs trained, accounts created |
| **14** | Dry run with full pipeline | All | End-to-end test passing |
| **15** | Pilot goes live | All | System monitoring farmers |
| **15** | Begin monitoring pilot KPIs | Data Analyst | Weekly KPI reports |
| **16** | Collect initial results, first pilot evaluation | Project Lead | Preliminary results report |

### Post-Week 16 (ongoing)

- Continue monitoring throughout crop season
- Monthly KPI reviews
- Model recalibration as new data arrives
- RM feedback collection
- Prepare management presentation with control group results

---

## 16. Team & Roles

### Core PoC team (8–10 people)

| Role | FTE | Responsibilities | Source |
|------|-----|------------------|--------|
| **Project Lead** | 1 | Overall delivery, stakeholder management, reporting | Internal (Innovation/Digital) |
| **Data Engineer (Geo)** | 1 | Satellite ingestion, GIS processing, spatial data pipeline | Internal or contract |
| **Data Engineer (Financial)** | 1 | Sathapana CBS/loan system integration, feature pipeline | Internal |
| **ML Engineer** | 1 | Crop health models, credit risk models, SHAP | Internal or contract |
| **Frontend Engineer** | 1 | Dashboard, map views, alert UI | Internal or contract |
| **Backend Engineer** | 1 | API services, scoring pipeline, workflow | Internal or contract |
| **Data Analyst** | 1 | KPI tracking, validation analysis, reporting | Internal |
| **Credit Risk SME** | 0.5 | Target variable definition, threshold calibration, business validation | Internal (Credit Risk) |
| **RM Liaison** | 0.5 | GPS collection coordination, field observations, RM training | Internal (Branch Ops) |

### External support (if needed)

| Role | Engagement | Purpose |
|------|-----------|---------|
| Remote sensing consultant | Part-time (4–6 weeks) | Satellite pipeline design, model advisory |
| GIS specialist | Part-time (2–3 weeks) | Boundary detection, spatial analysis |
| Cloud architect | Part-time (1–2 weeks) | Infrastructure design and security review |

### RACI matrix

| Activity | Project Lead | Data Eng | ML Eng | Frontend | Credit Risk | RM Liaison |
|----------|:-----------:|:--------:|:------:|:--------:|:-----------:|:----------:|
| Portfolio selection | A | C | I | I | R | C |
| GPS collection | A | I | I | I | I | R |
| Satellite pipeline | A | R | C | I | I | I |
| Financial integration | A | R | I | I | C | I |
| Farm mapping model | A | C | R | I | C | C |
| Crop health model | A | C | R | I | C | C |
| Risk model | A | C | R | I | R | C |
| Dashboard | A | C | C | R | C | I |
| Alert system | A | R | C | R | C | I |
| KPI tracking | A | I | C | I | C | C |
| RM training | R | I | I | I | C | R |

*R = Responsible, A = Accountable, C = Consulted, I = Informed*

---

## 17. Budget Estimate

### 16-week PoC budget

#### Personnel

| Role | Duration | Monthly Rate (USD) | Total (USD) |
|------|----------|--------------------:|------------:|
| Project Lead (internal, 50%) | 4 months | — (existing) | 0* |
| Data Engineer — Geo (contract) | 4 months | $4,000–6,000 | $16,000–24,000 |
| Data Engineer — Financial (internal) | 4 months | — (existing) | 0* |
| ML Engineer (contract) | 4 months | $5,000–8,000 | $20,000–32,000 |
| Frontend Engineer (contract) | 3 months | $4,000–6,000 | $12,000–18,000 |
| Backend Engineer (contract) | 3 months | $4,000–6,000 | $12,000–18,000 |
| Data Analyst (internal) | 4 months | — (existing) | 0* |
| Credit Risk SME (internal, 25%) | 4 months | — (existing) | 0* |
| RM Liaison (internal, 25%) | 4 months | — (existing) | 0* |
| Remote sensing consultant | 6 weeks | $6,000–8,000/mo | $9,000–12,000 |
| **Personnel subtotal** | | | **$69,000–104,000** |

*Internal staff costs absorbed by existing departments. Contract rates are estimates for Cambodia/regional market.*

#### Infrastructure

| Item | Monthly (USD) | Duration | Total (USD) |
|------|---------------:|----------|------------:|
| Cloud compute (processing) | $300–500 | 4 months | $1,200–2,000 |
| Cloud compute (dashboard) | $100–200 | 3 months | $300–600 |
| Cloud storage | $50–100 | 4 months | $200–400 |
| Database (managed) | $100–200 | 4 months | $400–800 |
| Google Earth Engine | Free tier | — | $0 |
| Sentinel data | Free (Copernicus) | — | $0 |
| Weather data (CHIRPS) | Free | — | $0 |
| **Infrastructure subtotal** | | | **$2,100–3,800** |

#### Other costs

| Item | Cost (USD) | Notes |
|------|------------:|-------|
| GPS devices (5x) | $500–1,500 | For RM farm boundary collection |
| Mobile data (field collection) | $200–400 | SIM cards for GPS collection |
| RM travel (field validation) | $1,000–2,000 | Mileage for farm visits |
| Software licenses | $500–1,000 | Mapping tools, design tools |
| Training materials | $200–500 | RM training, documentation |
| Contingency (15%) | $11,000–17,000 | Unexpected costs |
| **Other subtotal** | | **$13,400–22,400** |

### Total PoC budget

| Category | Low (USD) | High (USD) |
|----------|----------:|-----------:|
| Personnel | $69,000 | $104,000 |
| Infrastructure | $2,100 | $3,800 |
| Other | $13,400 | $22,400 |
| **Total** | **$84,500** | **$130,200** |

### Budget note

This is a **PoC budget**, not a production deployment. The goal is to validate the concept with minimal investment before committing to a full-scale rollout.

If the PoC succeeds, a production deployment would require:
- Dedicated cloud infrastructure
- Production-grade security and compliance
- Full-time team
- Integration with Sathapana core systems
- Estimated production budget: $300,000–500,000 (Year 1)

---

## 18. Risk & Mitigation

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|:----------:|:------:|------------|
| 1 | **Cloud cover prevents usable satellite observations during wet season** | High | Medium | Use Sentinel-1 SAR (works through clouds); build temporal composites; accept reduced optical coverage in wet season |
| 2 | **GPS data collection is slow or incomplete** | Medium | High | Start collection early (Week 2); provide simple mobile app; incentivize RM participation; accept ~80% coverage as minimum |
| 3 | **Insufficient historical data for model training** | High | Medium | Use rule-based scoring initially; back-test with satellite archive; transition to ML as data accumulates |
| 4 | **Sathapana systems integration is difficult** | Medium | High | Engage IT early; define minimal data extract; use flat files if APIs unavailable |
| 5 | **RMs do not adopt the dashboard** | Medium | High | Involve RM lead in design; make dashboard actionable (not just informational); provide training; collect feedback iteratively |
| 6 | **False positives erode trust** | Medium | Medium | Start with conservative thresholds; explain model outputs via SHAP; calibrate against field observations |
| 7 | **Farm boundary accuracy is poor** | Low | Medium | Use GPS as primary source; satellite as validation; accept lower accuracy for initial pilot |
| 8 | **Model does not generalize across provinces** | Medium | Medium | Build province-specific growth curves; stratify pilot across regions; recalibrate per province |
| 9 | **Stakeholder interest wanes during pilot** | Medium | High | Monthly executive updates; early wins visibility; demonstrate dashboard to leadership by Week 10 |
| 10 | **Regulatory/data privacy concerns** | Low | High | Consult compliance early; anonymize data where possible; document data governance; ensure farmer consent |

---

## 19. Governance & Ethics

### Data governance

- All farmer data must be handled per Sathapana's data protection policies
- Satellite data is publicly available (no privacy concern)
- Financial data access restricted to authorized team members
- Farmer consent required for GPS collection and monitoring
- Data retention policies aligned with Sathapana records management

### Model governance

- Model decisions are **advisory only** — no automated lending or collections actions
- All risk scores are explained via SHAP values
- Model is subject to periodic review and recalibration
- Bias monitoring: ensure model does not discriminate by geography, gender, or other protected attributes
- Human override: RM can override any AI-generated alert or recommendation

### Ethical considerations

- Farmers should be informed that their farms are being monitored as part of the loan program
- The system is designed to **help** farmers (early intervention, restructuring support), not to penalize them
- Control group farmers receive normal service — no disadvantage
- Model outputs should not be used to deny credit without human review
- Cultural and local context must be considered in farmer interactions

### Compliance

- Align with National Bank of Cambodia regulations on credit risk management
- Comply with Sathapana's internal credit policy
- Document model development and validation per regulatory expectations
- Ensure audit trail for all model decisions

---

## 20. Post-PoC Roadmap

### If PoC succeeds

```
PoC (16 weeks)
     │
     ▼
Management review + decision
     │
     ├── Expand to additional provinces
     ├── Add crop types (cassava, corn, vegetables)
     ├── Integrate deeper into loan origination
     ├── Production infrastructure
     └── Full team build-out
           │
           ▼
Phase 2 (6–12 months)
     │
     ├── Scale to full agricultural portfolio
     ├── Automated early-warning workflows
     ├── Insurance integration
     ├── Mobile farmer dashboard
     └── Partnership with satellite providers
           │
           ▼
Phase 3 (12–24 months)
     │
     ├── Predictive yield forecasting
     ├── Price risk integration
     ├── Supply-chain visibility
     ├── Regional expansion (CLMV)
     └── API for third-party lenders
```

### Phase 2 enhancements

| Enhancement | Description |
|-------------|-------------|
| Multi-crop support | Rice, cassava, corn, soybean, vegetables |
| Automated farm boundary detection | CV model for satellite-based parcel segmentation |
| Yield forecasting | Predict harvest volume and quality |
| Price risk integration | Commodity price monitoring |
| Insurance integration | Parametric crop insurance triggers |
| Mobile farmer app | Farmers can view their farm health status |
| Deeper CBS integration | Real-time transaction features |
| Production-grade ML pipeline | MLOps, model versioning, A/B testing |

### Phase 3 vision

| Capability | Description |
|------------|-------------|
| Regional expansion | Extend to Laos, Myanmar, Vietnam |
| API platform | Offer agricultural risk data to other lenders |
| Supply-chain visibility | Track crops from farm to buyer |
| Carbon credit monitoring | Verify agricultural carbon offset projects |
| Climate resilience scoring | Long-term farm viability assessment |

---

## 21. Appendix

### A. Key references

| # | Reference | Relevance |
|---|-----------|-----------|
| 1 | FAO Cambodia — GEO-AI for Agriculture Workshop | AI-based rice-field mapping demonstrated in Cambodia using Sentinel-2 |
| 2 | World Bank — Cambodia Digital Agriculture Assessment | Agricultural credit scoring identified as validated use case |
| 3 | ADB Project 50264-002 — Agricultural Value Chain Competitiveness | Sathapana Bank participating in agricultural value-chain project |
| 4 | BIIA — Satellite Tech Helps Cambodian Farmers Access Low-Interest Loans | Existing Cambodian market example of satellite data for lending decisions |
| 5 | Zhang et al. (2026) — Mekong-Tonle Sap Rice Yield Study | Sentinel-1 + Sentinel-2 used for rice mapping in the Mekong region |
| 6 | World Bank — AgriConnect FAQ | AI + satellite for smallholder crop monitoring guidance |
| 7 | Copernicus Open Access Hub | Free Sentinel-1 and Sentinel-2 data access |

### B. Glossary

| Term | Definition |
|------|-----------|
| NDVI | Normalized Difference Vegetation Index — measures vegetation greenness/density |
| NDWI | Normalized Difference Water Index — measures vegetation water content |
| EVI | Enhanced Vegetation Index — similar to NDVI, less sensitive to soil background |
| SAR | Synthetic Aperture Radar — cloud-penetrating satellite radar |
| IoU | Intersection over Union — measure of polygon overlap accuracy |
| DPD | Days Past Due — number of days a payment is overdue |
| NPL | Non-Performing Loan — loan where borrower has stopped making payments |
| AUC | Area Under the ROC Curve — model discrimination metric |
| SHAP | SHapley Additive exPlanations — model interpretability method |
| CBS | Core Banking System |
| RM | Relationship Manager |
| CHIRPS | Climate Hazards Group InfraRed Precipitation with Station data |
| ERA5 | ECMWF Reanalysis v5 — global weather/climate reanalysis dataset |
| MRC | Mekong River Commission |
| GEE | Google Earth Engine |

### C. Sentinel-2 band reference

| Band | Wavelength (nm) | Resolution | Use |
|------|-----------------|------------|-----|
| B2 (Blue) | 490 | 10m | Atmospheric correction |
| B3 (Green) | 560 | 10m | NDWI, vegetation |
| B4 (Red) | 665 | 10m | NDVI, chlorophyll |
| B5 (Red Edge 1) | 705 | 20m | Crop type, stress |
| B6 (Red Edge 2) | 740 | 20m | LAI, canopy |
| B7 (Red Edge 3) | 783 | 20m | Vegetation |
| B8 (NIR) | 842 | 10m | NDVI, biomass |
| B8A (NIR narrow) | 865 | 20m | Water vapor |
| B11 (SWIR 1) | 1610 | 20m | NDWI, moisture |
| B12 (SWIR 2) | 2190 | 20m | Soil/vegetation |
| SCL | Scene Classification | 20m | Cloud/shadow masking |

### D. Sentinel-1 band reference

| Polarization | Use |
|-------------|-----|
| VV | Surface scattering, flood detection |
| VH | Volume scattering, crop structure |
| VH/VV ratio | Crop type, moisture |

---

## 22. Feasibility Assessment — Will This Work for Sathapana?

### Question

> Do you think this platform works for Sathapana Bank?

### Answer

Honestly — **it has strong potential, but there are real risks that could kill it if not managed carefully.**

---

### What makes it work for Sathapana specifically

**Structural advantages:**

- 175 branches across Cambodia = existing RM network to collect GPS data and do field validation
- ADB agricultural value-chain project participation = management already understands agri-lending risk
- Award-winning mobile app (Sathapana Mobile) = digital culture exists internally
- Japanese parent (MARUHAN) = technology investment appetite
- $2.7B total assets = budget for a $85–130K PoC is trivial

**Cambodia-specific feasibility:**

- FAO has already demonstrated AI rice-mapping with Sentinel-2 in Cambodia — this isn't theoretical
- A Cambodian agri-fintech is already selling satellite-based farm data to lenders
- Sentinel-2 + Sentinel-1 data covers all of Cambodia freely
- Rice is the dominant crop — focusing on one crop simplifies the model significantly

---

### Where it could fail

#### 1. GPS data collection is the critical bottleneck

This is the single biggest risk. The entire platform depends on knowing *where each farmer's farm actually is*. Collecting GPS boundaries for 500–1,000 farmers across rural Cambodia in weeks 2–4 is ambitious. RMs are busy. Farmers may be hard to reach. GPS devices may not work well in dense vegetation.

If you can't get reliable farm boundaries, Stage 2 collapses.

**Mitigation:** Start with 200 farms, not 1,000. Use satellite-based parcel detection as a fallback. Consider a simple mobile app that RMs can use with their phones.

#### 2. Cloud cover during wet season

Cambodia's wet season (May–October) has heavy cloud cover. Sentinel-2 optical imagery becomes unreliable. The PoC would likely run during this period.

SAR (Sentinel-1) helps, but it's less intuitive for crop health than optical indices like NDVI.

**Mitigation:** Design the pipeline to degrade gracefully — use SAR when optical is unavailable, accept reduced observation frequency, and focus on dry-season satellite data for historical baselines.

#### 3. No historical data for model training

At PoC start, you have zero labeled data linking satellite signals to actual loan outcomes. The model will be weak initially.

**Mitigation:** Start with rule-based scoring (not ML). Use historical satellite archive to back-test. Transition to ML once you have a season of data. Be upfront with management that the model improves over time.

#### 4. RM adoption

The dashboard is only useful if RMs actually use it. If it's just another system they have to check, it will be ignored.

**Mitigation:** Make alerts actionable (not just scores), integrate into existing RM workflows, show RM names on alerts, track adoption metrics, and iterate based on RM feedback.

#### 5. Cambodia's small farm parcels

Average farm size in Cambodia is 1–3 hectares. At 10m Sentinel-2 resolution, that's 100–300 pixels per farm. Boundary detection is harder than for large-scale farming in, say, Brazil or the US.

**Mitigation:** GPS collection as primary, satellite as validation. Accept lower satellite boundary accuracy for small farms.

---

### Feasibility rating

| Factor | Rating | Note |
|--------|:------:|------|
| Technical feasibility | 7/10 | Sentinel data + Cambodia rice mapping is proven |
| Data availability | 6/10 | GPS collection is the bottleneck |
| Sathapana fit | 8/10 | Strong branch network, digital culture, agri exposure |
| Cambodian context | 7/10 | FAO validation exists, but cloud cover is real |
| PoC timeline realism | 5/10 | 16 weeks is tight — 20 weeks is safer |
| Business case clarity | 9/10 | Early warning → avoid NPL is a clear bank value prop |
| Risk of failure | Medium | GPS collection and RM adoption are the make-or-break factors |

---

### Recommended approach: Start smaller

**Don't pitch a 16-week PoC.** Pitch a **6-week feasibility study** first.

```
Week 1–2:  Select 50 farms, collect GPS, validate satellite data
Week 3–4:  Build pipeline for those 50 farms, generate crop health scores
Week 5–6:  Compare satellite signals vs. actual farm conditions (RM field visits)
           Present results to management
```

**Feasibility study parameters:**

| Parameter | Value |
|-----------|-------|
| Cost | $15,000–25,000 |
| Duration | 6 weeks |
| Team | 3 people (1 data engineer, 1 ML engineer, 1 RM liaison) |
| Sample | 50 farms, 1 province, rice only |
| Output | Proof that satellite signals correspond to real farm conditions |

If those 50 farms produce credible results, *then* pitch the full 16-week PoC with budget and team. That's a much easier management sell than asking for $130K and 10 people on a concept.

### Bottom line

> **The platform is sound. The risk is execution, not concept. Start smaller, prove it works on 50 farms, then scale.**

---

## 23. GPS Data Collection — How to Get Farm Coordinates

### Question

> How to get GPS coordinates of farmers' land? This is so critical for Stage 2.

### Answer

This is the make-or-break question. Here are the practical options, ranked by feasibility for Cambodia.

---

### Tier 1 — Most practical for PoC

#### 1. RM walks boundary with phone GPS (primary method)

RMs already visit farms at loan origination. Add a 10-minute GPS collection step.

**How it works:**

- RM opens a simple mobile form (Sathapana Mobile feature or lightweight web app)
- Taps "Start GPS recording"
- Walks the farm boundary
- Taps "Stop" when done
- Polygon is saved to the cloud

**Pros:** Uses existing RM network, no new hardware, high accuracy
**Cons:** RM must actually walk the boundary (not just stand at the entrance), adds ~10 min per farm visit

**Cambodia reality:** Most RMs carry smartphones. Sathapana already has a mobile app. Adding a GPS collection module to Sathapana Mobile is realistic.

#### 2. Farmer pins farm center via SMS/USSD

For farmers with basic phones (not smartphones):

- Farmer sends SMS with farm location code
- System sends back a USSD prompt: "Press 1 for rice, 2 for cassava..."
- RM follows up to collect exact boundary on next visit

**Pros:** Works on feature phones, high coverage
**Cons:** Only gets center point, not boundary — sufficient for Stage 2 NDVI analysis but not precise area measurement

#### 3. Community-based mapping

Work with village chiefs or agricultural cooperatives:

- Village chief identifies farm locations on a printed satellite map
- Farmer confirms by pointing
- RM digitizes the coordinates

**Pros:** Leverages local knowledge, fast for large areas
**Cons:** Less precise, depends on village chief cooperation

---

### Tier 2 — Supplementary / validation

#### 4. Satellite-based automatic parcel detection

Use CV to detect farm boundaries from Sentinel-2 or higher-resolution imagery:

- OpenStreetMap has some Cambodia farmland data
- FAO's rice mapping model for Cambodia could be adapted
- Commercial providers (Descartes Labs, Orbital Insight) offer parcel data

**Pros:** No field work needed, covers entire country
**Cons:** 10m Sentinel resolution is too coarse for 1–3 hectare Cambodian farms; commercial data is expensive

**Recommendation for PoC:** Use as validation, not primary source.

#### 5. Government land registry (LMAP)

Cambodia's Land Management and Administration Project (LMAP) has digitized land titles in some provinces:

- Contains parcel boundaries and ownership
- Available for titled land

**Pros:** Official data, already digitized in some areas
**Cons:** Coverage is incomplete, access may require government partnerships, not all agricultural land is titled

#### 6. Drone mapping

For high-value pilot farms:

- RM or field officer flies a consumer drone (DJI Mini, ~$300)
- Captures geotagged photos
- Software stitches into orthomosaic with GPS coordinates

**Pros:** Very high accuracy, visual proof
**Cons:** Requires drone + operator, regulatory considerations, slow for many farms

**Recommendation:** Use for 10–20 validation farms, not mass collection.

---

### Tier 3 — Future / experimental

#### 7. Farmer self-service via app

Simple app where farmer:

- Opens map, sees satellite view of their area
- Taps corners of their farm
- System saves polygon

**Pros:** Scalable, no RM visit needed
**Cons:** Requires smartphone, digital literacy, may not work in rural Cambodia

#### 8. IoT/GPS trackers

Deploy GPS loggers on farm equipment or livestock that also serve as farm location markers.

**Pros:** Passive data collection
**Cons:** Expensive, impractical for smallholders, over-engineering

---

### Recommended PoC approach

```
PRIMARY METHOD
    │
    ▼
RM walks boundary with phone GPS
(Sathapana Mobile or lightweight web app)
    │
    ├── 500 farms
    ├── 10 min per farm
    ├── Polygon saved to cloud
    └── Validates against loan record area
    │
    ▼
VALIDATION METHOD
    │
    ▼
Satellite parcel detection (Sentinel-2 + CV)
    │
    ├── Cross-check GPS polygons
    ├── Flag discrepancies > 20%
    └── Use as backup for failed GPS collections
    │
    ▼
HIGH-ACCURACY SAMPLE
    │
    ▼
Drone mapping (20 farms)
    │
    ├── Ground truth for model calibration
    └── Validate both GPS and satellite methods
```

### Method comparison

| Method | Time per farm | Cost per farm | Accuracy | Scale |
|--------|:------------:|:-------------:|:--------:|:-----:|
| RM + phone GPS | 10–15 min | ~$0 (existing RM time) | High | 500+ |
| Farmer SMS/USSD | 2 min | ~$0.10 | Low (center only) | 1,000+ |
| Satellite detection | Automated | ~$0 | Medium | Unlimited |
| Government LMAP | Lookup | ~$0 | High (where available) | Varies |
| Drone | 30–60 min | ~$5–10 | Very high | 20–50 |

### Critical insight

> **You don't need perfect GPS boundaries for Stage 2 to work.** NDVI analysis works at the farm level with a center point + approximate area. A 10m error in boundary does not materially affect crop health scoring. Perfect boundaries matter for area-based lending decisions, but not for early warning.

**Start with center points if boundary walking is too slow, then upgrade to full polygons as the pilot matures.**

---

### E. Free Data Source URLs — Quick Reference

| # | Data Source | URL | Auth Required | GEE Collection ID |
|---|-------------|-----|:--------------:|-------------------|
| 1 | Sentinel-2 Optical | https://dataspace.copernicus.eu/ | GEE auth | `COPERNICUS/S2_SR_HARMONIZED` |
| 2 | Sentinel-1 SAR | https://dataspace.copernicus.eu/ | GEE auth | `COPERNICUS/S1_GRD` |
| 3 | MODIS Land Cover | https://earthengine.google.com/ | GEE auth | `MODIS/061/MCD12Q1` |
| 4 | CHIRPS Rainfall | https://data.chc.ucsb.edu/products/CHIRPS-2.0/ | None | N/A (REST) |
| 5 | ERA5 Temperature | https://cds.climate.copernicus.eu/ | Free registration | N/A (CDS API) |
| 6 | Cambodia Boundaries | https://gadm.org/download_country.html | None | N/A (shapefile) |
| 7 | MRC Flood Data | https://portal.mrcmekong.org/ | Free registration | N/A (REST API) |
| 8 | Landsat 8/9 | https://landsat.gsfc.nasa.gov/ | GEE auth | `LANDSAT/LC08/C02/T1_L2` |
| 9 | OpenStreetMap | https://www.openstreetmap.org/ | None | N/A |
| 10 | WorldPop | https://www.worldpop.org/ | None | N/A |
| 11 | Soil Grids | https://soilgrids.org/ | None | N/A |
| 12 | FAO Crop Calendar | https://www.fao.org/giews/countrybrief/country.jsp?KHM | None | N/A |
| 13 | Google Earth Engine | https://earthengine.google.com/ | Free registration | Platform |
| 14 | Copernicus Browser | https://browser.dataspace.copernicus.eu/ | Free registration | Viewer |
| 15 | GEE Code Editor | https://code.earthengine.google.com/ | GEE auth | IDE |

### F. GEE Setup for Cambodia

```bash
# 1. Sign up for GEE (free)
# https://earthengine.google.com/

# 2. Create GCP project
# https://console.cloud.google.com/

# 3. Enable Earth Engine API in GCP Console

# 4. Install Python API
pip install earthengine-api

# 5. Authenticate
earthengine authenticate

# 6. Set environment variable
export GEE_PROJECT_ID="your-project-id"

# 7. Verify with Cambodia bounds
python -c "
import ee
ee.Initialize(project='your-project-id')
collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterDate('2026-06-01', '2026-09-01')
  .filterBounds(ee.Geometry.Rectangle([102, 10, 108, 15]))
print(f'Cambodia Sentinel-2 images: {collection.size().getInfo()}')
"
```

### G. Env Vars Template

```bash
# Backend (.env)
GEE_PROJECT_ID=
CHIRPS_API_URL=https://data.chc.ucsb.edu/products/CHIRPS-2.0
ERA5_API_URL=https://cds.climate.copernicus.eu/api
ERA5_API_KEY=
MRC_API_URL=
USE_SQLITE=true
DATABASE_URL=postgresql://sarp:sarp123@localhost:5432/sarp
JWT_SECRET=change-me-in-production
SMTP_HOST=
SMTP_USER=
SMTP_PASSWORD=
```

---

## 24. Do Banks Really Need External Data for Farmers?

### Question

> Do banks really need to use external data like satellite imagery and weather data for agricultural lending? Can't they just use internal loan and transaction data?

### Answer

**It depends on the bank's context.** Not every bank needs external data. Some manage agricultural lending perfectly well with internal data and RM visits alone.

---

### When Banks DO Need External Data

| Situation | Why Internal Data Isn't Enough |
|-----------|-------------------------------|
| **Remote farms** with infrequent RM visits | Bank only sees the loan, not the crop |
| **Climate-vulnerable regions** (flood/drought-prone) | Mekong basin has 5–8 major floods per decade |
| **Large agricultural portfolios** | Cannot visit every farm regularly |
| **High agricultural NPL rates** | Traditional scoring fails for agri loans |
| **No transaction data** (cash-based farmers) | Deposits/withdrawals do not reflect farm income |
| **Long crop cycles** (6–12 months) | Farm condition changes drastically between origination and harvest |

### When Banks DO NOT Need External Data

| Situation | Why Traditional Methods Work |
|-----------|----------------------------|
| **Strong RM network** with monthly farm visits | RM sees the crop firsthand |
| **Small portfolio** (fewer than 100 agri borrowers) | RM can manage relationships personally |
| **Stable climate** zones | Low flood/drought risk |
| **Good internal data** (transactions, deposits) | Cash flow tells the story |
| **Short crop cycles** or diversified farming | Less concentration risk |
| **Small loan amounts** | Cost of monitoring exceeds potential loss |

### Decision Matrix: When External Data Is Worth It

| Factor | Worth It | Not Worth It |
|--------|----------|-------------|
| Portfolio size | >500 agri borrowers | <100 borrowers |
| Climate risk | Flood/drought prone | Stable weather |
| RM coverage | Cannot visit all farms | RMs visit monthly |
| NPL rate | >5% agricultural NPL | <2% agricultural NPL |
| Loan size | >$1,000 average | <$200 average |
| Transaction data | Poor (cash-based) | Good (digital payments) |
| Management appetite | Innovation budget available | Cost-constrained |

### The Core Problem External Data Solves

```
BEFORE (internal data only):

Farmer → Loan → [BLACK BOX: no visibility into farm] → Missed payment → NPL
                                                          (too late)

WITH EXTERNAL DATA:

Farmer → Loan → Satellite monitoring + Weather
    → Crop stress detected 30+ days early
    → RM intervention → Restructuring
    → Potentially avoid NPL
```

The fundamental gap is **visibility**. Between loan origination and maturity (6–12 months for rice), the bank has **no continuous signal** about what is happening on the farm. Internal data (deposits, transactions) only reflects financial behavior, not agricultural reality.

### Cost-Benefit Reality

| Metric | Without External Data | With External Data |
|--------|----------------------|-------------------|
| Monitoring cost per farm | ~$0 (RM visit time only) | ~$5–10/year (satellite is free, system cost amortized) |
| Visibility into crop | None between RM visits | Continuous (every 5–12 days) |
| Early warning lead time | 0 days (only after missed payment) | 30–60 days |
| False positive rate | N/A (no alerts) | 15–20% |
| NPL avoidance potential | 0% | 10–20% relative reduction (hypothesis) |

### Bottom Line

> **External data is not universally necessary — it is a force multiplier for banks with specific characteristics: large agricultural portfolios, climate-vulnerable regions, limited RM coverage, and cash-based borrowers.**
>
> For a bank like Sathapana in Cambodia, the case is strong: climate risk + cash-based farmers + large portfolio + $0 data cost. For a bank in Thailand with good weather and digital payments, internal data alone may suffice.

---

## 25. Mandatory External Data Sources for Sathapana

### Question

> Which external data sources are truly mandatory for Sathapana Bank? Are all 7 sources in §6 necessary?

### Answer

**Not all 7 are mandatory.** For Sathapana specifically, 3 free satellite/weather sources + 1 boundary download form the complete minimum viable external data stack. Total cost: **$0**.

---

### Mandatory (Must Have)

| # | Source | Why It's Non-Negotiable | Cost |
|---|--------|------------------------|------|
| 1 | **Sentinel-2** | Without optical satellite, there is no remote monitoring at all. NDVI is the single most important signal for crop health. | Free |
| 2 | **Sentinel-1** | Cambodia's wet season (May–Oct) has **5+ months of cloud cover**. Without SAR, you lose optical data for half the year. SAR is the only way to see through clouds. | Free |
| 3 | **CHIRPS Rainfall** | Drought and flood are the #1 and #2 crop killers in Cambodia. Rainfall deviation is the strongest environmental predictor of repayment stress. | Free |

### Highly Valuable (Strongly Recommended)

| # | Source | Why | Cost |
|---|--------|-----|------|
| 4 | **GADM Boundaries** | Needed once to map province/district levels. Download once, cache forever. | Free |
| 5 | **MRC Flood Data** | Cambodia-specific. Mekong floods directly affect Sathapana's Battambang/Siem Reap portfolio. But CHIRPS partially covers this. | Free |

### Nice to Have (Incremental Value)

| # | Source | What It Adds | Skip If... |
|---|--------|-------------|------------|
| 6 | **ERA5 Temperature** | Heat/cold stress detection. But temperature is less variable than rainfall in tropical Cambodia. | Budget is tight |
| 7 | **MODIS Land Cover** | Baseline cropland classification. But Sentinel-2 provides better resolution (10m vs 500m). | Sentinel-2 already covers it |
| 8 | **OpenStreetMap** | Road networks for logistics. Not relevant for credit risk. | Not needed |
| 9 | **WorldPop** | Population density. Not relevant for farm-level monitoring. | Not needed |
| 10 | **Soil Grids** | Soil properties. Not relevant for short-term crop monitoring. | Not needed |

---

### Minimum Viable External Data Stack

```
┌─────────────────────────────────────────────────┐
│           MANDATORY (3 sources, all free)         │
│                                                  │
│  Sentinel-2  →  NDVI, NDWI, EVI (crop health)   │
│  Sentinel-1  →  Flood detection through clouds   │
│  CHIRPS      →  Rainfall deviation (drought/     │
│                  flood early warning)             │
│                                                  │
│           + 1 one-time download                  │
│                                                  │
│  GADM        →  Cambodia province boundaries     │
│                                                  │
│           = 4 free data sources total            │
└─────────────────────────────────────────────────┘
```

### Why These 3 Are Enough

For Sathapana's core problem — *"Can we detect crop stress before the farmer misses a payment?"* — the signal chain is:

```
Satellite detects NDVI decline (Sentinel-2)
        ↓
Cloud cover blocks optical (May–Oct)
        ↓
SAR continues monitoring (Sentinel-1)
        ↓
Rainfall deviation confirms drought/flood (CHIRPS)
        ↓
Combined signal = early warning
        ↓
30+ days before missed payment
```

**Remove any one of these three and the system breaks:**

| Remove... | What Breaks |
|-----------|-------------|
| Sentinel-2 | No NDVI, no crop health signal at all |
| Sentinel-1 | Blind for 5+ months during wet season |
| CHIRPS | Cannot distinguish "crop healthy but drought coming" from "crop healthy and fine" |

### When Is External Data Worth It vs. Not?

| Factor | Worth It | Not Worth It |
|--------|----------|-------------|
| Portfolio size | >500 agri borrowers | <100 borrowers |
| Climate risk | Flood/drought prone | Stable weather |
| RM coverage | Cannot visit all farms | RMs visit monthly |
| NPL rate | >5% agricultural NPL | <2% agricultural NPL |
| Loan size | >$1,000 average | <$200 average |
| Transaction data | Poor (cash-based) | Good (digital payments) |
| Management appetite | Innovation budget available | Cost-constrained |

### Sathapana-Specific Assessment

```
✅ 175 branches across Cambodia     → RM network exists, but cannot cover all farms
✅ $2.7B total assets                → Budget for monitoring
✅ Agricultural/SME exposure         → Significant risk
✅ Cambodia = flood/drought prone    → Climate risk is real
✅ Average farm 1-3 hectares         → Hard to monitor manually
✅ Wet season (May-Oct)              → Cloud cover limits RM visits
✅ Cash-based farmers                → Internal data is incomplete
```

**Conclusion for Sathapana:** The 3 mandatory sources (Sentinel-2 + Sentinel-1 + CHIRPS) are worth it because:
- RM visits alone cannot cover hundreds of thousands of km² of rural Cambodia
- Internal transaction data is incomplete for cash-based farmers
- A single Mekong flood can wipe out 50+ farms in a week
- The PoC cost ($85–130K) is trivial against a $2.7B balance sheet
- Total external data cost: **$0** (all free)

---

### Bottom Line

> **3 free satellite/weather sources + 1 boundary download = complete external data stack for Sathapana. Total cost: $0.**
>
> Everything else (ERA5, MODIS, MRC, OSM) adds incremental value but the system works without them.

The SPEC's 7 external sources are comprehensive, but **Sentinel-2 + Sentinel-1 + CHIRPS** are the minimum viable set. Everything else is optimization.

---

## 26. How to Get Cambodian Data from Sentinel-2 and Sentinel-1

### Question

> How do we actually get satellite data for Cambodia from Sentinel-2 and Sentinel-1? What are the practical steps?

### Answer

There are **3 methods**, from easiest to most flexible. All are free.

---

### Method 1: Google Earth Engine (Recommended)

**Best for:** Analysis, processing, no download needed. Data stays in the cloud.

#### Setup (5 minutes)

```bash
# 1. Sign up (free for research/non-commercial)
# https://earthengine.google.com/

# 2. Install Python API
pip install earthengine-api

# 3. Authenticate (opens browser)
earthengine authenticate

# 4. Verify Cambodia coverage
python -c "
import ee
ee.Initialize()
collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \\
  .filterDate('2026-06-01', '2026-09-01') \\
  .filterBounds(ee.Geometry.Rectangle([102, 10, 108, 15]))
print(f'Cambodia images: {collection.size().getInfo()}')
"
```

#### Get NDVI for a Specific Farm

```python
import ee
ee.Initialize(project='your-project-id')

# Farm coordinates (example: Battambang province)
lat, lon = 13.1, 103.2
point = ee.Geometry.Point([lon, lat])

# Get latest cloud-free Sentinel-2 image
image = (
    ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(point)
    .filterDate('2026-08-01', '2026-09-10')
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
    .sort('CLOUDY_PIXEL_PERCENTAGE')
    .first()
)

# Compute NDVI = (B8 - B4) / (B8 + B4)
ndvi = image.normalizedDifference(['B8', 'B4'])

# Get NDVI value at farm location
value = ndvi.reduceRegion(
    ee.Reducer.mean(), point.buffer(100), 10
).get('nd')

print(f'NDVI: {value.getInfo():.3f}')
# Output: NDVI: 0.723 (healthy rice)
```

#### Get All Indices at Once

```python
import ee
ee.Initialize()

lat, lon = 13.1, 103.2
point = ee.Geometry.Point([lon, lat])

image = (
    ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(point)
    .filterDate('2026-08-01', '2026-09-10')
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
    .first()
)

# NDVI
ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')

# NDWI
ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI')

# EVI = 2.5 * (NIR - RED) / (NIR + 6*RED - 7.5*BLUE + 1)
evi = image.expression(
    '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
    {
        'NIR': image.select('B8'),
        'RED': image.select('B4'),
        'BLUE': image.select('B2'),
    }
).rename('EVI')

# Sample all at point
result = ee.Dictionary({
    'ndvi': ndvi.reduceRegion(ee.Reducer.mean(), point.buffer(100), 10).get('NDVI'),
    'ndwi': ndwi.reduceRegion(ee.Reducer.mean(), point.buffer(100), 10).get('NDWI'),
    'evi': evi.reduceRegion(ee.Reducer.mean(), point.buffer(100), 10).get('EVI'),
    'date': image.date().format('YYYY-MM-dd').getInfo(),
}).getInfo()

print(f"Date: {result['date']}")
print(f"NDVI:  {result['ndvi']:.3f}")
print(f"NDWI:  {result['ndwi']:.3f}")
print(f"EVI:   {result['evi']:.3f}")
```

#### Get Sentinel-1 SAR Data

```python
import ee
ee.Initialize()

lat, lon = 13.1, 103.2
point = ee.Geometry.Point([lon, lat])

# Sentinel-1 GRD (Ground Range Detected)
sar = (
    ee.ImageCollection('COPERNICUS/S1_GRD')
    .filterBounds(point)
    .filterDate('2026-08-01', '2026-09-10')
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
    .filter(ee.Filter.eq('instrumentMode', 'IW'))
    .first()
)

# VV = surface scattering, VH = volume scattering
vv = sar.select('VV').reduceRegion(
    ee.Reducer.mean(), point.buffer(100), 10
).get('VV')

vh = sar.select('VH').reduceRegion(
    ee.Reducer.mean(), point.buffer(100), 10
).get('VH')

print(f"VV backscatter: {vv.getInfo():.2f} dB")
print(f"VH backscatter: {vh.getInfo():.2f} dB")
print(f"VH/VV ratio:    {vh.getInfo() - vv.getInfo():.2f} dB")
```

#### Visualize Cambodia in Code Editor

```javascript
// Paste in GEE Code Editor: https://code.earthengine.google.com/

Map.setCenter(104.9, 12.5, 7); // Cambodia center

// Sentinel-2 true color
var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterDate('2026-06-01', '2026-09-01')
  .filterBounds(ee.Geometry.Rectangle([102, 10, 108, 15]))
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
  .median();

Map.addLayer(s2, {bands: ['B4','B3','B2'], min: 0, max: 3000}, 'True Color');

// NDVI
var ndvi = s2.normalizedDifference(['B8', 'B4']);
Map.addLayer(ndvi, {min: -0.2, max: 0.8, palette: ['red','yellow','green']}, 'NDVI');

// Sentinel-1 SAR
var s1 = ee.ImageCollection('COPERNICUS/S1_GRD')
  .filterBounds(ee.Geometry.Rectangle([102, 10, 108, 15]))
  .filterDate('2026-06-01', '2026-09-01')
  .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
  .select('VV')
  .median();

Map.addLayer(s1, {min: -25, max: 0}, 'SAR VV');
```

---

### Method 2: Copernicus Data Space (Direct Download)

**Best for:** Downloading raw GeoTIFF files for offline analysis.

#### Setup

```bash
# 1. Register (free)
# https://dataspace.copernicus.eu/

# 2. Install CLI
pip install sentinelsat
```

#### Search for Cambodia Scenes

```python
from sentinelsat import SentinelAPI
from datetime import date

api = SentinelAPI('username', 'password', 'https://apihub.copernicus.eu/apihub')

# Cambodia bounding box
products = api.query(
    area='POLYGON((102 10, 108 10, 108 15, 102 15, 102 10))',
    date=(date(2026, 8, 1), date(2026, 9, 10)),
    platformname='Sentinel-2',
    cloudcoverpercentage=(0, 20),
    producttype='S2MSI2A',  # Level-2A (surface reflectance)
)

print(f'Found {len(products)} scenes')
for uuid, props in list(products.items())[:5]:
    print(f"  {props['title']} | Cloud: {props['cloudcoverpercentage']:.1f}%")
```

#### Download a Scene

```python
api.download(uuid, directory='./data/sentinel2/')
```

---

### Method 3: Python + GEE API (Best for Pipeline)

**Best for:** Automated data pipeline in the SARP backend.

```python
import ee
from datetime import date, timedelta

ee.Initialize(project='your-project-id')

def get_cambodia_farm_data(lat, lon, start_date, end_date):
    """Fetch all satellite data for a Cambodia farm."""

    point = ee.Geometry.Point([lon, lat])
    bbox = ee.Geometry.Rectangle([lon - 0.05, lat - 0.05, lon + 0.05, lat + 0.05])

    # --- Sentinel-2 ---
    s2 = (
        ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
        .filterBounds(point)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
        .sort('CLOUDY_PIXEL_PERCENTAGE')
        .first()
    )

    ndvi = s2.normalizedDifference(['B8', 'B4']).rename('NDVI')
    ndwi = s2.normalizedDifference(['B3', 'B8']).rename('NDWI')
    evi = s2.expression(
        '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
        {'NIR': s2.select('B8'), 'RED': s2.select('B4'), 'BLUE': s2.select('B2')}
    ).rename('EVI')

    # --- Sentinel-1 ---
    s1 = (
        ee.ImageCollection('COPERNICUS/S1_GRD')
        .filterBounds(point)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
        .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
        .first()
    )

    # Sample everything
    result = ee.Dictionary({
        'ndvi': ndvi.reduceRegion(ee.Reducer.mean(), point.buffer(100), 10).get('NDVI'),
        'ndwi': ndwi.reduceRegion(ee.Reducer.mean(), point.buffer(100), 10).get('NDWI'),
        'evi': evi.reduceRegion(ee.Reducer.mean(), point.buffer(100), 10).get('EVI'),
        'vv': s1.select('VV').reduceRegion(ee.Reducer.mean(), point.buffer(100), 10).get('VV'),
        'vh': s1.select('VH').reduceRegion(ee.Reducer.mean(), point.buffer(100), 10).get('VH'),
        'date': s2.date().format('YYYY-MM-dd').getInfo(),
        'cloud_cover': s2.get('CLOUDY_PIXEL_PERCENTAGE'),
    }).getInfo()

    return {
        'ndvi': round(float(result.get('ndvi', 0)), 4),
        'ndwi': round(float(result.get('ndwi', 0)), 4),
        'evi': round(float(result.get('evi', 0)), 4),
        'vv_db': round(float(result.get('vv', -12)), 2),
        'vh_db': round(float(result.get('vh', -18)), 2),
        'date': result.get('date'),
        'source': 'sentinel_gee',
    }

# Usage
data = get_cambodia_farm_data(13.1, 103.2, '2026-08-01', '2026-09-10')
print(data)
# {'ndvi': 0.723, 'ndwi': 0.18, 'evi': 0.65, 'vv_db': -11.2, 'vh_db': -16.8, ...}
```

---

### Which Method to Use

| Method | Best For | Difficulty | Cost |
|--------|----------|:----------:|:----:|
| **GEE Python API** | Automated pipeline in SARP | Medium | Free |
| **GEE Code Editor** | Visual exploration, prototyping | Easy | Free |
| **Copernicus Download** | Raw GeoTIFF files for offline analysis | Harder | Free |

**Recommendation for Sathapana:** Use **Method 3 (GEE Python API)** — it integrates directly into the SARP backend, processes data in the cloud, and does not require downloading massive GeoTIFF files.

---

## 27. Automated GEE Data Ingestion Pipeline

### Question

> How do we automatically fetch real Sentinel data for all pilot farms on a schedule?

### Answer

A fully automated pipeline has been built into the SARP backend. It fetches real Sentinel-2 and Sentinel-1 data from Google Earth Engine for every farm in the database, computes spectral indices, calculates the Crop Health Score, and stores results as records.

---

### Pipeline Architecture

```
┌─────────────────────────────────────────────────┐
│          GEE INGESTION PIPELINE                  │
│                                                  │
│  For each farm in database:                      │
│    1. Fetch Sentinel-2 (NDVI, NDWI, EVI)        │
│    2. Fetch Sentinel-1 (VV, VH backscatter)     │
│    3. Fetch weather (rainfall, temperature)      │
│    4. Compute Crop Health Score (weighted)       │
│    5. Create CropHealth record in DB             │
│                                                  │
│  If GEE_PROJECT_ID set → REAL satellite data     │
│  If not set            → SIMULATED fallback      │
│                                                  │
│  Batch: commits every 10 farms for efficiency    │
└─────────────────────────────────────────────────┘
```

### What the Pipeline Fetches Per Farm

| Step | Data Source | Indices Computed |
|------|-----------|------------------|
| 1 | Sentinel-2 (GEE) | NDVI, NDWI, EVI |
| 2 | Sentinel-1 (GEE) | VV backscatter, VH backscatter, VH/VV ratio |
| 3 | CHIRPS rainfall | 30-day rainfall total, deviation from normal |
| 4 | ERA5 temperature | Average temp, stress days (>38°C) |
| 5 | Crop Health Score | Weighted composite: NDVI(30%) + Trend(20%) + NDWI(15%) + SAR(10%) + Rain(15%) + Temp(10%) |

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `POST /api/gee/ingest` | POST | Run ingestion for ALL farms |
| `POST /api/gee/ingest/{farm_id}` | POST | Ingest single farm |
| `GET /api/gee/status` | GET | Check GEE config + observation counts |
| `GET /api/gee/test-connection` | GET | Test if GEE is reachable |
| `GET /api/gee/fetch-farm/{farm_id}` | GET | Preview satellite data (no DB save) |
| `GET /api/gee/cambodia-coverage` | GET | Check Sentinel image count over Cambodia |

### Scheduler Integration

The pipeline runs automatically on a schedule via APScheduler:

| Job | Schedule | Purpose |
|-----|----------|---------|
| GEE Ingestion | Every 6 hours | Fetch latest Sentinel-2/1 for all farms |
| Weather Ingestion | Daily 06:00 UTC | Fetch CHIRPS rainfall + ERA5 temperature |
| Risk Scoring | Daily 07:00 UTC | Re-score all farmers with ML model |
| Model Re-training | Weekly Sunday 02:00 UTC | Retrain model with accumulated data |
| Notifications | Daily 08:00 UTC | Send RM email digests |

### Code Example: Fetch Data for One Farm

```python
from app.services.gee_ingestion import fetch_sentinel2_for_farm, fetch_sentinel1_for_farm
from datetime import date

# Fetch Sentinel-2 for a farm in Battambang
s2 = fetch_sentinel2_for_farm(
    lat=13.1, lon=103.2,
    start_date=date(2026, 8, 1),
    end_date=date(2026, 9, 10),
)
print(f"NDVI: {s2['ndvi']}, Source: {s2['source']}")
# When GEE configured: NDVI: 0.723, Source: sentinel2_gee
# When not configured: NDVI: 0.75, Source: simulated

# Fetch Sentinel-1 SAR
s1 = fetch_sentinel1_for_farm(13.1, 103.2, date(2026, 8, 1), date(2026, 9, 10))
print(f"VV: {s1['vv_db']}dB, VH: {s1['vh_db']}dB")
```

### Code Example: Run Full Ingestion

```python
from app.services.gee_ingestion import run_full_ingestion
from app.database import SessionLocal

db = SessionLocal()
result = run_full_ingestion(db)
print(result)
# {
#   'total_farms': 154,
#   'successful': 154,
#   'failed': 0,
#   'data_sources': {'sentinel2_gee': 154, 'sentinel1_gee': 154},
#   'gee_enabled': True,
#   'status': 'real_data',
# }
```

### How to Enable Real Data

```bash
# 1. Get GEE project ID (see §26 for setup steps)

# 2. Set environment variable
export GEE_PROJECT_ID="your-project-id"

# 3. Start the backend
python run.py

# 4. Trigger ingestion manually
curl -X POST http://localhost:8000/api/gee/ingest

# 5. Verify real data is flowing
curl http://localhost:8000/api/gee/status
# → "gee_enabled": true, "status": "real_data"
```

### Verified Output (Simulated Mode)

```
=== Ingestion Status ===
  gee_enabled: False
  total_farms: 154
  total_observations: 2772
  latest_observation: 2026-09-10
  status: simulated_data

=== Batch Ingestion ===
  Total: 154
  Success: 154
  Failed: 0
  Sources: simulated: 154
```

### Expected Output (Real GEE Mode)

```
=== Ingestion Status ===
  gee_enabled: True
  gee_project: sathapana-poc-2026
  total_farms: 154
  total_observations: 4312
  latest_observation: 2026-09-10
  status: real_data

=== Batch Ingestion ===
  Total: 154
  Success: 154
  Failed: 0
  Sources: sentinel2_gee: 154, sentinel1_gee: 154
```

### Error Handling

| Scenario | Behavior |
|----------|----------|
| GEE not configured | Falls back to simulated data, logs warning |
| GEE auth fails | Falls back to simulated data, logs error |
| No Sentinel-2 images for farm | Falls back to simulated data |
| No Sentinel-1 images for farm | Falls back to simulated data |
| Single farm fails | Logs error, continues with next farm |
| Network timeout | Retries once, then skips farm |

### File Locations

| File | Purpose |
|------|---------|
| `app/services/gee_ingestion.py` | Core pipeline — fetch, compute, store |
| `app/routes/gee.py` | API endpoints |
| `app/services/scheduler.py` | APScheduler job definitions |
| `app/services/crop_health_score.py` | Weighted score formula |
| `app/services/weather.py` | CHIRPS + ERA5 data fetch |

---

*Document version: 1.6*
*Last updated: September 2026*
*Author: Innovation Lab*
*Status: Draft for Management Review*
