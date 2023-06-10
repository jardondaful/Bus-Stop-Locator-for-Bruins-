import arcpy

# Take user input legal address
address = input("Enter the full, legal address: ")

# Set up locator
url = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer"
locator = arcpy.geocoding.GeocodeServer(url)

print("Starting geocode")

# Actual geocoding process
result = locator.geocodeAddresses([address], outSR=arcpy.SpatialReference(4326))

# Check if geocoding was successful
if 'locations' in result:
    location = result['locations'][0]['location']
    latitude = location['y']
    longitude = location['x']
    
    # Create a new shapefile
    output_folder = r"C:\path\to\output\folder"  # Specify the desired output folder path
    output_shapefile = "geocoded_point.shp"  # Specify the output shapefile name
    
    arcpy.env.workspace = output_folder
    arcpy.management.CreateFeatureclass(output_folder, output_shapefile, "POINT", spatial_reference=arcpy.SpatialReference(4326))
    
    # Create a new feature and insert the point
    with arcpy.da.InsertCursor(output_shapefile, ['SHAPE@XY']) as cursor:
        cursor.insertRow([(longitude, latitude)])
    
    print("Shapefile created successfully.")
else:
    print("Geocoding failed.")

print("Done geocoding")
