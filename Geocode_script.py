# This script geocodes the user input to Lat/Lon output
# to my knowledge and understanding this process should NOT consume credits
# there is no error handling. This code accepts full legal address only

import arcpy

# take user input legeal address
address = input("Enter the full, legal address: ")

# Set up locator 
url = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/ArcGIS World Geocoding Service"
locator = arcpy.geocoding.Locator(url)

print("starting geocode")

# actuall geocoding process 
result = locator.geocode(address, True)

# Get latitude and longitude from geocoding results
for item in result:
    shape = item['Shape']
    Latitude = shape.Y
    Longitude = shape.X
    
print("Latitude: {}, Longitude: {}".format(Latitude, Longitude))
    

print("done gocoding")
