import arcpy
import requests

def geocode_address(address):
    # Set up geocoding service URL
    url = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates"

    # Create the request payload
    params = {
        "SingleLine": address,
        "f": "json",
        "outSR": "4326"
    }

    # Send the request and retrieve the response
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        # Check if there are any candidates found
        if "candidates" in data:
            # Get the first candidate
            candidate = data["candidates"][0]

            # Extract the latitude and longitude
            location = candidate["location"]
            latitude = location["y"]
            longitude = location["x"]

            print("Latitude: {}, Longitude: {}".format(latitude, longitude))

            # Create a new shapefile
            output_folder = r"C:\Users\rmiramo214\Desktop\181C Final Project\MyProject26\MyProject26"
            output_shapefile = "Geocoded_point.shp"
            arcpy.env.workspace = output_folder
            arcpy.management.CreateFeatureclass(output_folder, output_shapefile, "POINT", spatial_reference=arcpy.SpatialReference(4326))

            # Create a new feature and insert the point
            with arcpy.da.InsertCursor(output_shapefile, ['SHAPE@XY']) as cursor:
                cursor.insertRow([(longitude, latitude)])

            print("Shapefile created successfully.")
        else:
            print("No candidates found.")
    else:
        print("Request failed.")

    print("Done geocoding")

# Example usage
address = "581 Gayle Ave, Los Angeles, CA"
geocode_address(address)
