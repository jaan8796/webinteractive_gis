from pathlib import Path
import geopandas as gpd, json, random
from shapely.geometry import Point
root=Path(__file__).resolve().parents[1]; out=root/'data/processed'
p=gpd.read_file(root/'data/input/Parcel.shp'); b=gpd.read_file(root/'data/input/Buildings.shp')
print('gov land types',p.LUSE_DET.value_counts().loc[lambda x:x.index.str.contains('Govt|Government',case=False,na=False)].to_dict())
print('build types',b.LUSE_DET.value_counts().head(12).to_dict())
# Clearly labelled demonstration attributes, never asserted as measured data.
seed=random.Random(44)
pg=p[p.LUSE_DET.astype(str).str.contains('State Govt|Central Govt|Municipal',case=False,na=False)].copy()
if len(pg)<5: pg=p[p.LUSE_DET.astype(str).str.contains('Govt',case=False,na=False)].copy()
pg=pg.head(24).copy()
statuses=['Occupied','Partially occupied','Vacant - sample']; utilization=['In use','Underutilised - sample','Not assessed']; agencies=['Municipal office - sample','State department - sample','Agency not verified']
for i,idx in enumerate(pg.index):
 pg.at[idx,'agency_demo']=agencies[i%3];pg.at[idx,'occupancy_demo']=statuses[i%3];pg.at[idx,'utilisation_demo']=utilization[i%3];pg.at[idx,'development_demo']=['Existing','Potential review','Not assessed'][i%3];pg.at[idx,'encroachment_demo']='Not verified';pg.at[idx,'record_type']='DEMONSTRATION_ONLY';pg.at[idx,'ownership_verified']='NO'
pg.to_crs(4326).to_file(out/'GovernmentLandSample.geojson',driver='GeoJSON')
# Building demonstration inventory: only source buildings where landuse explicitly government-related, fallback small demonstration subset
bg=b[b.LUSE_DET.astype(str).str.contains('Govt|Government|Municipal',case=False,na=False)].copy()
if len(bg)<8: bg=b.head(18).copy()
bg=bg.head(30).copy()
for i,idx in enumerate(bg.index):
 bg.at[idx,'agency_demo']=agencies[i%3];bg.at[idx,'occupancy_demo']=statuses[i%3];bg.at[idx,'utilisation_demo']=utilization[i%3];bg.at[idx,'development_demo']=['Existing','Repair review','Not assessed'][i%3];bg.at[idx,'encroachment_demo']='Not verified';bg.at[idx,'record_type']='DEMONSTRATION_ONLY';bg.at[idx,'ownership_verified']='NO'
bg.to_crs(4326).to_file(out/'GovernmentBuildingSample.geojson',driver='GeoJSON')
# Synthetic sample slums, deliberately not claims of real settlement locations; placed within municipality for UI testing
mun=gpd.read_file(root/'data/input/MunicipalBoundary.shp').to_crs(4326)
poly=mun.geometry.iloc[0]; bounds=poly.bounds
pts=[]
for fx,fy in [(.36,.4),(.53,.56),(.63,.38),(.45,.7),(.58,.48),(.34,.6)]:
 pt=Point(bounds[0]+(bounds[2]-bounds[0])*fx,bounds[1]+(bounds[3]-bounds[1])*fy)
 if poly.contains(pt):pts.append(pt)
 if len(pts)==3:break
if len(pts)<3:
 pts=[poly.representative_point()]*3
records=[]
for i,pt in enumerate(pts):
 records.append({'slum_id':f'DEMO-SL-{i+1:02}','name':f'Sample settlement {i+1} (synthetic)','population_sample':[420,650,310][i],'land_status_sample':['Unverified','Under review','Unverified'][i],'water_access_sample':['Partial','Unknown','Partial'][i],'sanitation_sample':['Partial','Unknown','Limited'][i],'road_access_sample':['Nearby','Unknown','Nearby'][i],'record_type':'SYNTHETIC_DEMONSTRATION_NOT_REAL_LOCATION','geometry':pt.buffer(.0014)})
sl=gpd.GeoDataFrame(records,crs='EPSG:4326');sl.to_file(out/'SlumSampleSynthetic.geojson',driver='GeoJSON')
# desktop GIS evidence, linked to actual source parcel ID; no claim of field inspection
sel=p[p.LUSE_DET.eq('Open Land')].iloc[0]; sid=str(sel.PCL_ID)
rec={'record_id':'DESKTOP-OBS-001','feature_type':'Parcel','feature_id':sid,'source_layer':'Parcel','source_field':'LUSE_DET','source_value':str(sel.LUSE_DET),'observation':'Source land-use classification is Open Land; parcel selected for follow-up review.','method':'Desktop GIS attribute review','evidence_reference':'data/input/Parcel.dbf; data/processed/Parcel.geojson','verification':'Not field verified','ownership':'Not established','inspection_photo':None,'date_type':'Processing example; not a field visit'}
(root/'evidence/Desktop_Observation_001.json').write_text(json.dumps(rec,indent=2),encoding='utf-8')
print('demo gov land',len(pg),'gov buildings',len(bg),'slums',len(sl),'evidence',sid)
