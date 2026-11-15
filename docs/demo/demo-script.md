# Five-minute demo script

## 1. Start and set expectations

Run `python scripts/start_demo.py`, open `http://127.0.0.1:8000`, and point out the persistent `DEMO DATA — NOT REAL ENVIRONMENTAL ANALYSIS` banner. Explain that the supplied example row is a placeholder retained from the source ZIP and is used only to exercise the interface.

## 2. Show the farmer flow

Choose English, Urdu, or Sindhi; continue as guest; place the pin in the Hyderabad pilot; select cotton, water source/availability, salinity/waterlogging inputs, and a priority. Submit an example request. Explain that the three cards demonstrate the existing rule-based rotation engine and do not represent field-validated outcomes.

## 3. Show evidence and limitations

Open the context/expert view. Show the real SRTM slope overlay and its source/date/resolution metadata. Show the SMAP and GPM regional context and explain that the source periods are not aligned. Identify missing NDVI/NDMI/BSI/thermal layers and the unavailable K-Means cluster as missing, not inferred.

## 4. Show weather and persistence

Point out the “Saved forecast sample” label, valid period, and not-live state. Show the analysis ID and reload endpoint (or reload the saved analysis). Explain that real mode returns forecast unavailable if live credentials/service are not available.

## 5. Close with the data gate

The exact Landsat scene files (SR bands, ST_B10, QA_PIXEL and MTL) must be supplied before a real multi-point feature file can be built. After inspection and validation, run the feature builder, evaluate K-Means on at least 20 complete unique points, review neutral cluster profiles with an agronomist, then rerun all real-data scenarios. No trained model metrics or real recommendation quality claims are part of this demo.
