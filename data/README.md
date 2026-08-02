# Geospatial Property Data & SRO Feeds (`data/`)

This directory contains the geospatial, demographic, market trend, and Sub-Registrar Office (SRO) property transaction feeds for the **Crown Corridor** platform across Andhra Pradesh and Telangana.

## 📂 Directory Structure

```
data/
├── andhra_pradesh/        # AP regional datasets (districts, mandals, villages, market trends)
│   ├── andhra_pradesh_districts.json
│   ├── andhra_pradesh_mandals.json
│   ├── andhra_pradesh_villages.json
│   ├── andhra_pradesh_coords.json
│   ├── andhra_pradesh_meta.json
│   └── andhra_pradesh_market_trends.json
├── telangana/             # TS regional datasets (districts, mandals, villages, market trends)
│   ├── telangana_districts.json
│   ├── telangana_mandals.json
│   ├── telangana_villages.json
│   ├── telangana_coords.json
│   ├── telangana_meta.json
│   └── telangana_market_trends.json
├── sro_feed/              # Automated Sub-Registrar Office transaction logs
│   ├── telangana_sro_2026-07-20.json
│   └── ...
├── benchmarks/            # Benchmark datasets and evaluation ground truths
└── property_history.json  # Comprehensive property sales history & CAGR metrics
```

## 🔒 Zero-PII Compliance Requirements

All datasets strictly follow **Zero-PII Privacy Compliance**:
- **No Personal Identifiers**: Customer personal names, phone numbers, email addresses, or individual IDs are strictly prohibited.
- **Anonymized Classification**: Transactions use standardized owner classifications (`Private Individual Owner`, `Commercial Property Developer`, `Institutional Realty Fund`).
- **Validation**: Run `python3 pipeline/validate_data.py` to verify data schemas and zero-PII compliance across all JSON files.
