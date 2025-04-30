import pandas as pd
import geopandas as gpd
import folium

# Load the GeoJSON file
geojson_file = 'up_districts.geojson'
gdf = gpd.read_file(geojson_file)
gdf['district'] = gdf['district'].str.lower().str.strip()

# Create a base map centered around Uttar Pradesh
up_map = folium.Map(location=[27.0, 80.0], zoom_start=6)

# Define a list of CSV files and their display names
csv_files = {
    'dataa.csv': 'Data A',
    'datab.csv': 'Data B',
    'datac.csv': 'Data C',
    'datad.csv': 'Data D',
    'datae.csv': 'Data E',
    'dataf.csv': 'Data F'
}

# Define the columns you want to toggle between
data_columns = [
    'Fire Hazard', 'Heavy Rainfall', 'Storms and Winds', 'Lightening',
    'Drowning', 'Gas Leak', 'Cyclone', 'Boat Accident', 'Flash Floods',
    'Fell in Borewell', 'Killed by Animal', 'Snake Bite', 'Coldwave',
    'Sewer Cleaning', 'Total Casualties'
]

# Function to add the choropleth layer
def add_choropleth(data_file, column):
    data = pd.read_csv(data_file, encoding='ISO-8859-1')
    data['District'] = data['District'].fillna('').str.lower().str.strip()
    merged_gdf = gdf.merge(data, how='left', left_on='district', right_on='District')

    # Create a new choropleth layer
    choropleth = folium.Choropleth(
        geo_data=merged_gdf,
        data=merged_gdf,
        columns=['district', column],
        key_on='feature.properties.district',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=column
    )
    choropleth.add_to(up_map)

    # Add tooltips to display district data
    tooltip = folium.GeoJson(
        merged_gdf,
        style_function=lambda x: {'fillColor': 'transparent', 'color': 'transparent'},
        tooltip=folium.GeoJsonTooltip(
            fields=['district', column],
            aliases=['District: ', f'{column}: '],
            labels=True,
            sticky=True
        )
    )
    tooltip.add_to(up_map)

# Add the initial choropleth layer using the first dataset and column
initial_file = list(csv_files.keys())[0]
initial_column = data_columns[0]
add_choropleth(initial_file, initial_column)

# Dropdown HTML for selecting datasets
dropdown_html = """
<div style="position: fixed; top: 10px; right: 10px; z-index: 9999;">
    <select id="dataset" onchange="updateMap()">
        <option value="dataa.csv">Data A</option>
        <option value="datab.csv">Data B</option>
        <option value="datac.csv">Data C</option>
        <option value="datad.csv">Data D</option>
        <option value="datae.csv">Data E</option>
        <option value="dataf.csv">Data F</option>
    </select>
    <select id="column" onchange="updateMap()">
        <option value="Fire Hazard">Fire Hazard</option>
        <option value="Heavy Rainfall">Heavy Rainfall</option>
        <option value="Storms and Winds">Storms and Winds</option>
        <option value="Lightening">Lightening</option>
        <option value="Drowning">Drowning</option>
        <option value="Gas Leak">Gas Leak</option>
        <option value="Cyclone">Cyclone</option>
        <option value="Boat Accident">Boat Accident</option>
        <option value="Flash Floods">Flash Floods</option>
        <option value="Fell in Borewell">Fell in Borewell</option>
        <option value="Killed by Animal">Killed by Animal</option>
        <option value="Snake Bite">Snake Bite</option>
        <option value="Coldwave">Coldwave</option>
        <option value="Sewer Cleaning">Sewer Cleaning</option>
        <option value="Total Casualties">Total Casualties</option>
    </select>
</div>
<script>
function updateMap() {
    var dataset = document.getElementById("dataset").value;
    var column = document.getElementById("column").value;
    // Use AJAX to fetch and update the map (placeholder alert for demo)
    alert("Selected Dataset: " + dataset + ", Column: " + column);
    // You would implement an AJAX call here to fetch new data and refresh the map
}
</script>
"""

# Add the dropdown HTML to the map
up_map.get_root().html.add_child(folium.Element(dropdown_html))

# Save the map to an HTML file
up_map.save('up_district_map_with_tooltips.html')

print("Map has been created and saved as 'up_district_map_with_tooltips.html'.")
