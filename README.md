# Nuzividu Municipal GIS — EY assignment

## Launch
1. Extract this archive.
2. Double-click `run_app.bat` (requires Python installed).
3. Visit http://localhost:8000/app/ in Chrome.
4. Keep the terminal window open. Internet is required for map tiles and Leaflet.

## Web map features
- Six original GIS layers: parcels, buildings, roads, revenue wards, landmarks, municipality.
- Base maps: OpenStreetMap, Carto Light, Carto Dark and **No basemap**.
- Parcel ID prefix search, building ID and OLD_H_NO house-number prefix search.
- Attribute filters by LUSE_DET and ward for parcels or buildings.
- Colour-coded parcel/building land-use categories, dynamic legend.
- Landmark labels (switch on; zoom to level 15+).
- Approximate road-proximity screening for a selected parcel.
- Source-identified government property demonstration subsets and synthetic slum examples.
- Parcel 100018000500001 has a linked **desktop GIS observation record** in its popup.

## Provenance
Original shapefiles are in `data/input`. Demonstration-only property statuses, agency names and slum attributes are **synthetic examples**, not official records or field-verified facts. The synthetic slum polygons are invented locations for demonstrating the interface, not known settlements. No photo or agency response has been supplied.

## Processing
`python -m pip install -r requirements.txt`
`python scripts/build_data.py`
`python scripts/generate_demonstration_data.py`

## Remaining assignment items
No live hosting, recording, real slum inventory, actual inspection photograph or authoritative property verification are included. Source area is **Nuzividu, Andhra Pradesh**, not Pune.


## Updated map tools (November 2026)
- Site surroundings: enter a full `PCL_ID` to find the nearest mapped road, nearest landmark, and nearest **main-road candidate** (source `RD_TYPE` codes 01/02). Distances are straight-line from the parcel centroid to the line or point, not travel distances. Road code meaning needs authoritative confirmation.
- Road buffer: search a road name or ID, select a particular segment, choose a buffer distance (25–500 m), and count parcel polygons intersecting that buffer. The count includes partially intersecting parcels.
- Home button: returns to the full municipality extent.
- Map legend: floats on the map and updates to reflect active layers and land-use categories visible within the current viewport.
- Basemap/layer selector: improved layout, with basemap choices including a blank/no-basemap option.

**Connectivity:** The road-buffer feature uses the open-source Turf.js library from an online CDN, in addition to Leaflet and basemap tile providers. Internet connectivity is required.
