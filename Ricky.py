import arcpy
import requests

def geocode_address(address, label):
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

            print("{} - Latitude: {}, Longitude: {}".format(label, latitude, longitude))

            return (longitude, latitude)  # Return the coordinates
        else:
            print("No candidates found.")
    else:
        print("Request failed.")

    return None  # Return None if geocoding fails


# Example usage
starting_address = "100 Hollywood Blvd, Los Angeles, CA"
desired_address = "200 S Grand Ave, Los Angeles, CA"

starting_coords = geocode_address(starting_address, "Starting Location")
desired_coords = geocode_address(desired_address, "Desired Location")

if starting_coords and desired_coords:
    # Create a new shapefilea
    output_folder = r"C:\Users\Jordan Lin\Downloads\GEOG_181C\MyProject26\MyProject26"
    output_shapefile = "geocoded_points.shp"
    arcpy.env.workspace = output_folder
    arcpy.management.CreateFeatureclass(output_folder, output_shapefile, "POINT", spatial_reference=arcpy.SpatialReference(4326))

    # Add a field to store the location labels
    arcpy.management.AddField(output_shapefile, "Location", "TEXT")

    # Create a new feature and insert the points
    with arcpy.da.InsertCursor(output_shapefile, ['SHAPE@XY', 'Location']) as cursor:
        cursor.insertRow([(starting_coords[0], starting_coords[1]), "Starting Location"])
        cursor.insertRow([(desired_coords[0], desired_coords[1]), "Desired Location"])

    print("Shapefile created successfully.")
