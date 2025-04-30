import pandas as pd
import folium
from folium.plugins import HeatMap
import geopandas as gpd
import branca

# Load CSV data
csv_file = "Book1.csv"  # Update with your file path
df = pd.read_csv(csv_file)

# Ensure Latitude and Longitude are numeric
df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

# Drop rows with invalid coordinates
df = df.dropna(subset=["Latitude", "Longitude"])

# Load GeoJSON data
geojson_file = "up_districts.geojson"  # Update with your file path
gdf = gpd.read_file(geojson_file)

# Convert DataFrame to GeoDataFrame
gdf_points = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude), crs=gdf.crs)

# Filter points within district boundaries
filtered_points = gdf_points[gdf_points.geometry.within(gdf.geometry.union_all())]

# Initialize the map centered around the data points
map_center = [filtered_points["Latitude"].mean(), filtered_points["Longitude"].mean()]
m = folium.Map(location=map_center, zoom_start=6, tiles="OpenStreetMap")

# Add Google Maps tile layer
folium.TileLayer(tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", attr="Google Maps", name="Google Maps").add_to(m)

# Add GeoJSON district boundaries with thinner black borders and increased transparency
folium.GeoJson(
    gdf, 
    name="District Boundaries", 
    style_function=lambda x: {"color": "black", "weight": 1, "fillOpacity": 0.1}  # Increased transparency
).add_to(m)

# Create heatmap layers for each unique waterbody type
waterbody_types = filtered_points["Waterbody"].unique()
heatmap_layers = {}

for waterbody in waterbody_types:
    waterbody_data = filtered_points[filtered_points["Waterbody"] == waterbody]
    heat_data = waterbody_data[["Latitude", "Longitude"]].values.tolist()
    heatmap_layer = folium.FeatureGroup(name=f"{waterbody} Heatmap")
    HeatMap(heat_data, radius=10, blur=15, gradient={0.2: "yellow", 0.4: "orange", 0.6: "red"}).add_to(heatmap_layer)
    heatmap_layer.add_to(m)
    heatmap_layers[waterbody] = heatmap_layer

# Add color scale for heatmap
colormap = branca.colormap.LinearColormap(
    colors=["yellow", "orange", "red"],
    vmin=0, vmax=len(filtered_points),
    caption="Heatmap Intensity"
)
colormap.add_to(m)

# Add toggleable markers with tooltips for waterbody locations
marker_layer = folium.FeatureGroup(name="Waterbody Locations")
for idx, row in filtered_points.iterrows():
    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        tooltip=row.get("Waterbody", "Unknown")
    ).add_to(marker_layer)
marker_layer.add_to(m)

# Add layer control to toggle heatmap and marker layers
folium.LayerControl().add_to(m)

# Save map to HTML file and display
m.save("heatmap.html")
print("Heatmap saved as heatmap.html. Open this file in a browser to view the map.")