import re

# Read index.html
with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# Extract all coordinate pairs using regex
# Coordinates look like [128.7600,35.8920] or [128.7540,35.8845]
coord_pattern = r'\[(128\.\d+),\s*(35\.\d+)\]'
matches = re.findall(coord_pattern, content)

lons = [float(lon) for lon, lat in matches]
lats = [float(lat) for lon, lat in matches]

if lons and lats:
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)
    print("GeoJSON Coordinates Bounds:")
    print(f"  Latitude:  {min_lat:.6f} to {max_lat:.6f}")
    print(f"  Longitude: {min_lon:.6f} to {max_lon:.6f}")
    
    # Let's add some margin (padding) to make sure everything fits comfortably inside
    margin_lat = (max_lat - min_lat) * 0.15
    margin_lon = (max_lon - min_lon) * 0.15
    print("\nSuggested Image Bounds (with 15% margin):")
    print(f"  South: {min_lat - margin_lat:.6f}")
    print(f"  West:  {min_lon - margin_lon:.6f}")
    print(f"  North: {max_lat + margin_lat:.6f}")
    print(f"  East:  {max_lon + margin_lon:.6f}")
else:
    print("No coordinates found!")
