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


# Take user input for addresses
starting_address = input("Enter the starting address: ")
desired_address = input("Enter the desired address: ")

starting_coords = geocode_address(starting_address, "Starting Location")
desired_coords = geocode_address(desired_address, "Desired Location")

if starting_coords and desired_coords:
    # Create a new shapefile
    output_folder = r"C:\Users\rmiramo214\Desktop\181C Final Project\MyProject1"
    output_shapefile = "geocoded_points.shp"
    arcpy.env.workspace = output_folder
    arcpy.env.overwriteOutput = True
    arcpy.management.CreateFeatureclass(output_folder, output_shapefile, "POINT", spatial_reference=arcpy.SpatialReference(4326))

    # Add a field to store the location labels
    arcpy.management.AddField(output_shapefile, "Location", "TEXT")

    # Create a new feature and insert the points
    with arcpy.da.InsertCursor(output_shapefile, ['SHAPE@XY', 'Location']) as cursor:
        cursor.insertRow([(starting_coords[0], starting_coords[1]), "Starting Location"])
        cursor.insertRow([(desired_coords[0], desired_coords[1]), "Desired Location"])

    print("Shapefile created successfully.")

# Name: MakeClosestFacilityAnalysisLayer_Workflow.py
# Description: Find the closest bus stop from the user location and save the
#              results to a layer file on disk.
# Requirements: Network Analyst Extension

#Import system modules
import arcpy
from arcpy import env
import os

try:
    #Check out Network Analyst license if available. Fail if the Network Analyst license is not available.
    if arcpy.CheckExtension("network") == "Available":
        arcpy.CheckOutExtension("network")
    else:
        raise arcpy.ExecuteError("Network Analyst Extension license is not available.")
    
    #Set environment settings
    #output_dir = "C:/Data"
    #The NA layer's data will be saved to the workspace specified here
    #env.workspace = os.path.join(output_dir, "Output.gdb")
    #env.overwriteOutput = True

    #Set environment settings
    #folder_path = r"C:\Users\julyquintero\Downloads\MyProject1" # output_dir
    folder_path = r"C:\Users\rmiramo214\Desktop\181C Final Project\MyProject1"
    ProjectGDB = os.path.join(folder_path, "MyProject1.gdb") 
    #The NA layer's data will be saved to the workspace specified here
    env.workspace = ProjectGDB #
    env.overwriteOutput = True


    #Set local variables
    #input_gdb = "C:/Data/Paris.gdb" #because already project GDB
    network = "https://www.arcgis.com/"
    layer_name = "ClosestBusStop" 
    travel_mode = "Walking Distance" 
    facilities = os.path.join(ProjectGDB, "TransitInfo", "StopsOnStreets")
###############
    ###########
    incidents = os.path.join(folder_path, output_shapefile)
###############
    ###########
    ###########
    output_layer_file = os.path.join(ProjectGDB, layer_name + ".lyrx")

    #Create a new closest facility analysis layer. 
    #result_object = arcpy.na.MakeClosestFacilityAnalysisLayer(network,
                                    #layer_name, travel_mode, "TO_FACILITIES",
                                    #number_of_facilities_to_find=1, generate_directions_on_solve="DIRECTIONS")


    #Create Closest Facility Analyst Layer
    #arcpy.ImportToolbox(r"@\Network Analyst Tools.tbx")
    result_object = arcpy.na.MakeClosestFacilityAnalysisLayer(
        network_data_source="https://www.arcgis.com/",
        layer_name="ClosestBusStop",
        travel_mode="Walking Distance",
        travel_direction="TO_FACILITIES",
        cutoff=2,
        number_of_facilities_to_find=1,
        time_of_day=None,
        time_zone="LOCAL_TIME_AT_LOCATIONS",
        time_of_day_usage="START_TIME",
        line_shape="ALONG_NETWORK",
        accumulate_attributes=None,
        generate_directions_on_solve="DIRECTIONS",
        ignore_invalid_locations="SKIP"
    )
    print("Creating a Closest Facility Analyst Layer ...")


    #Get the layer object from the result object. The closest facility layer can
    #now be referenced using the layer object.
    layer_object = result_object.getOutput(0)

    #Get the names of all the sublayers within the closest facility layer.
    sublayer_names = arcpy.na.GetNAClassNames(layer_object)
    #Stores the layer names that we will use later
    facilities_layer_name = sublayer_names["Facilities"]
    incidents_layer_name = sublayer_names["Incidents"]

    # Add this line to define directions_layer_name
    #directions_layer_name = sublayer_names["Directions"]

    #Load the bus stops as Facilities using the default field mappings and
    #search tolerance
    arcpy.na.AddLocations(layer_object, facilities_layer_name,
                            facilities, "", "")
    print("adding bus stop locations")

    #Load the user location as Incidents. Map the Name property from the NOM field
    #using field mappings
    field_mappings = arcpy.na.NAClassFieldMappings(layer_object,
                                                    incidents_layer_name)
    field_mappings["Name"].mappedFieldName = "NOM"
    arcpy.na.AddLocations(layer_object, incidents_layer_name, incidents,
                          field_mappings, "")
    print("loading user location")

    #Solve the closest facility layer
    arcpy.na.Solve(layer_object)

    #Save the solved closest facility layer as a layer file on disk
    layer_object.saveACopy(output_layer_file)

    print("Script completed successfully")

except Exception as e:
    # If an error occurred, print line number and error message
    import traceback, sys
    tb = sys.exc_info()[2]
    print("An error occurred on line %i" % tb.tb_lineno)
    print(str(e))

