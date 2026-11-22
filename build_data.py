"""Rebuild all six source GIS layers and a derived candidate open-land layer.
Run from any directory: python scripts/build_data.py
Requirements: geopandas, shapely, pandas, pyshp
Original shapefiles are never overwritten.
"""
from pathlib import Path
import json
import geopandas as gpd

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"data/input"
OUT=ROOT/"data/processed"
OUT.mkdir(parents=True,exist_ok=True)
NAMES=["Parcel","Buildings","RoadNetwork","RevenueWardBoundary","Landmarks","MunicipalBoundary"]
layers={}
qa={"study_area":"Nuzividu Municipality, Andhra Pradesh (TN_NAME source attribute)",
    "source_crs":"EPSG:32644","web_crs":"EPSG:4326",
    "feature_counts":{},"invalid_before_processing":{},"invalid_after_processing":{},
    "limitations":["Ownership and vacancy not independently verified",
                   "Slum and water-network data not supplied",
                   "No genuine field observation evidence supplied"]}
for name in NAMES:
    path=SRC/(name+".shp")
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}; all shapefile components required")
    gdf=gpd.read_file(path)
    if gdf.crs is None:
        raise ValueError(f"{name}: CRS undefined")
    if gdf.crs.to_epsg()!=32644:
        raise ValueError(f"{name}: unexpected CRS {gdf.crs}; verify before processing")
    qa["invalid_before_processing"][name]=int((~gdf.geometry.is_valid).sum())
    if name=="Parcel":
        gdf["geometry"]=gdf.geometry.make_valid()
    if name in ("Parcel","Buildings","RevenueWardBoundary","MunicipalBoundary"):
        gdf["area_calc_sqm"]=gdf.geometry.area.round(2)
    if name=="RoadNetwork":
        gdf["length_calc_m"]=gdf.geometry.length.round(2)
    gdf["data_origin"]="USER_SUPPLIED_SOURCE"
    gdf["verification_status"]="NOT_FIELD_VERIFIED"
    qa["feature_counts"][name]=len(gdf)
    qa["invalid_after_processing"][name]=int((~gdf.geometry.is_valid).sum())
    layers[name]=gdf
    web=gdf.copy()
    if name in ("Parcel","Buildings"):
        web["geometry"]=web.geometry.simplify(.3,preserve_topology=True)
    web.to_crs(4326).to_file(OUT/(name+".geojson"),driver="GeoJSON")
p=layers["Parcel"]
mask=p["LUSE_DET"].astype(str).str.fullmatch("Open Land",case=False,na=False)
candidates=p.loc[mask].copy()
candidates["analysis_status"]="CANDIDATE_OPEN_LAND_NOT_OWNERSHIP_VERIFIED"
# Open land remains a parcel land-use filter, not a separate map layer.
qa["open_land_candidate_count"]=len(candidates)
qa["open_land_candidate_area_sqm"]=round(float(candidates.geometry.area.sum()),2)
qa["road_length_km_geometry"]=round(float(layers["RoadNetwork"].geometry.length.sum()/1000),2)
qa["parcel_landuse_top12"]=p["LUSE_DET"].fillna("Unknown").value_counts().head(12).to_dict()
(OUT/"qa_summary.json").write_text(json.dumps(qa,indent=2),encoding="utf-8")
print(json.dumps(qa,indent=2))
